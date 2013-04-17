include Nanoc::Helpers::Rendering
include Nanoc::Helpers::Blogging
include Nanoc::Helpers::Tagging
include Nanoc::Helpers::LinkTo

include Nanoc::Toolbox::Helpers::Disqus
include Nanoc::Toolbox::Helpers::TaggingExtra

def tag_identifier(tag)
	"/blog/tag/#{tag.downcase.gsub(' ', '-')}"
end
