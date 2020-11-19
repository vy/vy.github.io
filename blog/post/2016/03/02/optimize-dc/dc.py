#!/usr/bin/env python

import logging
import math
import os
import re
import sys
import subprocess

logging_format = "%(asctime)s %(levelname)-8s %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def main():
	args = Args.fromArgv(sys.argv)
	logger.debug("reading setup: %s", args.dcFile)
	setup = Setup.fromDcFile(args.dcFile)
	logger.debug(setup)
	solve(args, setup)

def solve(args, setup):
	gl = args.g
	gr = int(math.ceil(sum(setup.serverCapacities) / float(setup.P)))
	gm = (gr + gl) / 2
	lastScore = 0
	while gm < gr:
		logger.info("solving for %d <= g=%d < %d", gl, gm, gr)
		problem = Problem(setup, gm)
		problemFile = args.problemFile(gm)
		logger.debug("writing problem: %s", problemFile)
		with Util.ensureOpen(problemFile) as pf:
			print >> pf, problem
		solver = Solver(args, setup, problem, problemFile)
		logger.debug("running solver")
		solution = solver.solve()
		if not solution:
			logger.debug("no solution")
			logger.debug("stepping back")
			gr = gm
		else:
			logger.debug("solution score: %d", solution.score)
			solutionFile = args.solutionFile(gm)
			logger.debug("writing solution: %s", solutionFile)
			with Util.ensureOpen(solutionFile) as sf:
				print >> sf, solution
			if not solution.score or solution.score < lastScore:
				logger.debug("stepping back")
				gr = gm
			else:
				logger.debug("stepping forward")
				gl = gm + 1
			lastScore = solution.score
		gm = (gr + gl) / 2

class Args:

	def __init__(self, cplexFile, dcFile, outputFilePrefix, g):
		self.cplexFile = cplexFile
		self.dcFile = dcFile
		self.outputFilePrefix = outputFilePrefix
		self.g = g

	def problemFile(self, g):
		return "{}-{}.lp".format(self.outputFilePrefix, g)

	def cplexOutputFile(self, g):
		return "{}-{}.out".format(self.outputFilePrefix, g)

	def solutionFile(self, g):
		return "{}-{}.soln".format(self.outputFilePrefix, g)

	@staticmethod
	def fromArgv(argv):
		if len(argv) != 5:
			print >> sys.stderr, "invalid arguments"
			print >> sys.stderr, "usage:", argv[0], "<CPLEX-FILE> <DC-FILE> <OUTPUT-FILE-PREFIX> <G>"
			sys.exit(1)
		return Args(argv[1], argv[2], argv[3], int(argv[4]))

class Setup:

	def __init__(self, R, S, U, P, M, unavailSlotCoords, serverSizes, serverCapacities):
		self.R = R
		self.S = S
		self.U = U
		self.P = P
		self.M = M
		self.unavailSlotCoords = unavailSlotCoords
		self.serverSizes = serverSizes
		self.serverCapacities = serverCapacities
		(self.availBlocks, self.availBlockCoords) = self.buildAvailBlocks()

	def buildAvailBlocks(self):
		unavailSlots = {}
		for [i, j] in self.unavailSlotCoords:
			if i not in unavailSlots: unavailSlots[i] = []
			unavailSlots[i].append(j)
		availBlocks = {}
		availBlockCoords = {}
		for i in range(self.R):
			if i not in unavailSlots:
				availBlocks[i] = [self.S]
				availBlockCoords[i] = {0: (0, self.S)}
			else:
				col = 0
				rowAvailBlocks = []
				rowAvailBlockCoords = {}
				js = sorted(unavailSlots[i])
				for (j1, j2) in zip([-1] + js, js + [self.S]):
					s = j2 - j1 - 1
					if s > 0:
						rowAvailBlocks.append(s)
						rowAvailBlockCoords[col] = (j1 + 1, j2)
						col += 1
				availBlocks[i] = rowAvailBlocks
				availBlockCoords[i] = rowAvailBlockCoords
		return (availBlocks, availBlockCoords)

	def __str__(self):
		return "R={}, S={}, U={}, P={}, M={}".format(self.R, self.S, self.U, self.P, self.M)

	@staticmethod
	def fromDcFile(dcFile):
		with open(dcFile) as handle:
			def readInts(): return map(int, handle.readline().strip().split())
			(R, S, U, P, M) = readInts()
			unavailSlotCoords = [readInts() for _ in range(U)]
			zcs = [readInts() for _ in range(M)]
			serverSizes = [item[0] for item in zcs]
			serverCapacities = [item[1] for item in zcs]
			return Setup(R, S, U, P, M, unavailSlotCoords, serverSizes, serverCapacities)

class Problem:

	def __init__(self, setup, g):
		self.setup = setup
		self.g = g
		self.lines = []
		self.addComments()
		self.addObjective()
		self.addConstraints()
		self.addVariables()
		self.lines.append("end")
		self.data = "\n".join(self.lines)

	def addComments(self):
		self.lines.append("\\ setup: {}".format(self.setup))
		self.lines.append("\\ g={}".format(self.g))

	def addObjective(self):
		self.lines.append("maximize")
		self.lines.append("  \\ dummy feasibility objective")
		objSumTokens = []
		for i in range(self.setup.R):
			for j in range(len(self.setup.availBlocks[i])):
				for k in range(self.setup.M):
					for l in range(self.setup.P):
						objSumTokens.append("a_{i}_{j}_{k}_{l}".format(**locals()))
		objSum = " + ".join(objSumTokens)
		self.lines.append("  {objSum}".format(**locals()))

	def addConstraints(self):
		self.lines.append("subject to")
		self.addServerPresenceConstraints()
		self.addBlockSizeConstraints()
		self.addPoolCapacityConstraints()

	def addServerPresenceConstraints(self):
		self.lines.append("  \\ a server can be assigned to at most 1 block and 1 pool")
		for k in range(self.setup.M):
			sumTokens = []
			for i in range(self.setup.R):
				for j in range(len(self.setup.availBlocks[i])):
					for l in range(self.setup.P):
						sumTokens.append("a_{i}_{j}_{k}_{l}".format(**locals()))
			suM = " + ".join(sumTokens)
			self.lines.append("  {suM} <= 1".format(**locals()))

	def addBlockSizeConstraints(self):
		self.lines.append("  \\ block sizes cannot be exceeded")
		for i in range(self.setup.R):
			c_i = self.setup.availBlocks[i]
			for j in range(len(c_i)):
				c_i_j = c_i[j]
				sumTokens = []
				for k in range(self.setup.M):
					z_k = self.setup.serverSizes[k]
					for l in range(self.setup.P):
						sumTokens.append("{z_k} a_{i}_{j}_{k}_{l}".format(**locals()))
				suM = " + ".join(sumTokens)
				self.lines.append("  {suM} <= {c_i_j}".format(**locals()))

	def addPoolCapacityConstraints(self):
		g = self.g
		self.lines.append("  \\ pool capacity constraints")
		totCapacitySums = {l: self.poolCapacitySum(l) for l in range(self.setup.P)}
		for l in range(self.setup.P):
			for i in range(self.setup.R):
				c_i = self.setup.availBlocks[i]
				rowCapacitySumTokens = []
				for k in range(self.setup.M):
					c_k = self.setup.serverCapacities[k]
					for j in range(len(c_i)):
						rowCapacitySumTokens.append("{c_k} a_{i}_{j}_{k}_{l}".format(**locals()))
				rowCapacitySum = " - ".join(rowCapacitySumTokens)
				totCapacitySum = totCapacitySums[l]
				self.lines.append("  {totCapacitySum} - {rowCapacitySum} >= {g}".format(**locals()))

	def poolCapacitySum(self, l):
		sumTokens = []
		for i in range(self.setup.R):
			for j in range(len(self.setup.availBlocks[i])):
				for k in range(self.setup.M):
					c_k = self.setup.serverCapacities[k]
					sumTokens.append("{c_k} a_{i}_{j}_{k}_{l}".format(**locals()))
		return " + ".join(sumTokens)

	def addVariables(self):
		self.lines.append("binary")
		for i in range(self.setup.R):
			for j in range(len(self.setup.availBlocks[i])):
				for k in range(self.setup.M):
					for l in range(self.setup.P):
						self.lines.append("a_{i}_{j}_{k}_{l}".format(**locals()))

	def __str__(self):
		return self.data

class Placement:

	def __init__(self, rowId, slotId, poolId):
		self.rowId = rowId
		self.slotId = slotId
		self.poolId = poolId

	def __repr__(self):
		return "({}, {}, {})".format(self.rowId, self.slotId, self.poolId)

class Solution:

	def __init__(self, setup, a):
		self.setup = setup
		self.a = a
		self.serverPlacements = self.findServerPlacements()
		self.score = self.findScore()
		self.validate()

	def findServerPlacements(self):
		poolIds = self.findPoolIds()
		placements = {}
		for i in range(self.setup.R):
			for j in range(len(self.setup.availBlocks[i])):
				ks = []
				for k in range(self.setup.M):
					for l in range(self.setup.P):
						if self.a[i][j][k][l]:
							ks.append(k)
				if ks:
					(j1, j2) = self.setup.availBlockCoords[i][j]
					for k in ks:
						if k not in poolIds:
							logger.warn("p[{k}][l] = 0 while a[{i}][{j}][{k}][l] = 1".format(**locals()))
						else:
							rowId = i
							slotId = j1
							poolId = poolIds[k]
							placement = Placement(rowId, slotId, poolId)
							if k in placements:
								existingPlacement = placements[k]
								raise Exception(
									"existing placement found for k={k}, was putting {placement}, found {existingPlacement}"
										.format(**locals()))
							placements[k] = placement
							j1 += self.setup.serverSizes[k]
							if j1 > j2:
								raise Exception(
									"block size exceeded (i, j, k, l) = ({i}, {j}, {k}, {poolId})"
										.format(**locals()))
		return placements

	def findPoolIds(self):
		poolIds = {}
		for i in range(self.setup.R):
			for j in range(len(self.setup.availBlocks[i])):
				for k in range(self.setup.M):
					for l in range(self.setup.P):
						if self.a[i][j][k][l]:
							if k not in poolIds: poolIds[k] = l
							else:
								v = poolIds[k]
								raise Exception(
									"poolIds[{k}] = {l} conflicts with previous set value: {v}"
										.format(**locals()))
		return poolIds

	def findScore(self):
		return min([self.findPoolGuaranteedCapacity(l) for l in range(self.setup.P)])

	def findPoolGuaranteedCapacity(self, l):
		totCapacity = self.findPoolCapacity(l)
		maxRowCapacity = max([self.findPoolRowCapacity(l, i) for i in range(self.setup.R)])
		return totCapacity - maxRowCapacity

	def findPoolCapacity(self, l):
		return sum([self.findPoolRowCapacity(l, i) for i in range(self.setup.R)])

	def findPoolRowCapacity(self, l, i):
		suM = 0
		for k in range(self.setup.M):
			c_k = self.setup.serverCapacities[k]
			for j in range(len(self.setup.availBlocks[i])):
				suM += c_k * self.a[i][j][k][l]
		return suM

	def validate(self):
		self.validateSlotAllocations()
		self.validatePoolAllocations()

	def validateSlotAllocations(self):
		slotAllocations = {}
		for (serverId, serverPlacement) in self.serverPlacements.items():
			place = (serverPlacement.rowId, serverPlacement.slotId)
			if place in slotAllocations:
				raise Exception(
					"invalid server placement: {}, was already allocated by server {}".format(
						serverPlacement, slotAllocations[place]))
			else: slotAllocations[place] = serverId

	def validatePoolAllocations(self):
		poolAllocations = {}
		for (serverId, serverPlacement) in self.serverPlacements.items():
			if serverId in poolAllocations:
				raise Exception(
					"invalid server placement: {}, was already allocated by pool".format(
						serverPlacement, poolAllocations[serverId]))
			else: poolAllocations[serverId] = serverPlacement.poolId

	def __str__(self):
		lines = []
		for k in range(self.setup.M):
			if k in self.serverPlacements:
				serverPlacement = self.serverPlacements[k]
				rowId = serverPlacement.rowId
				slotId = serverPlacement.slotId
				poolId = serverPlacement.poolId
				lines.append('{rowId} {slotId} {poolId}'.format(**locals()))
			else: lines.append('x')
		return "\n".join(lines)

class Solver():

	def __init__(self, args, setup, problem, problemFile):
		self.args = args
		self.setup = setup
		self.problem = problem
		self.problemFile = problemFile

	def solve(self):
		popen = subprocess.Popen(
			[self.args.cplexFile],
			stdin=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			stdout=subprocess.PIPE)
		inputTokens = [
			"read {} lp\n".format(self.problemFile),
			"set mip limits solutions 1",
			"set mip tolerances integrality 0",
			"set mip tolerances mipgap 0",
			"mipopt",
			"display solution variables *"]
		input = "\n".join(inputTokens)
		(stdoutdata, _) = popen.communicate(input)
		cplexOutputFile = self.args.cplexOutputFile(self.problem.g)
		logger.debug("writing cplex output: %s", cplexOutputFile)
		with Util.ensureOpen(cplexOutputFile) as cof:
			print >> cof, stdoutdata
		if "No integer feasible solution exists." in stdoutdata:
			return None
		returncode = popen.returncode
		if returncode:
			msg = "unexpected return code: {}".format(returncode)
			logger.error(msg)
			logger.error(stdoutdata)
			raise Exception(msg)
		return self.parseStdout(stdoutdata)

	def parseStdout(self, stdout):
		a = {i: {j: {k: {l: 0
			for l in range(self.setup.P)}
				for k in range(self.setup.M)}
					for j in range(len(self.setup.availBlocks[i]))}
						for i in range(self.setup.R)}
		for line in re.split('\r?\n', stdout):
			strippedLine = line.strip()
			match = re.match('^a_(\d+)_(\d+)_(\d+)_(\d+)\s+1.000000$', strippedLine)
			if match:
				(i, j, k, l) = map(int, match.groups())
				if not a[i][j][k][l]: a[i][j][k][l] = 1
				else: raise Exception("a[{i}][{j}][{k}][{l}] has already been set".format(**locals()))
		return Solution(self.setup, a)

class Util:

	@staticmethod
	def ensureOpen(pathname, mode="w"):
		dirname = os.path.dirname(pathname)
		if len(dirname) > 1 and not os.path.exists(dirname):
			os.makedirs(dirname)
		return open(pathname, mode)

if __name__ == "__main__": main()
