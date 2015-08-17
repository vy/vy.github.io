---
kind: article
created_at: 2015-08-15 15:25 CEST
title: Scala Shortcuts for Vaadin Development
tags:
  - scala
  - vaadin
---

This year I had found chance to get my hands dirty with
[Vaadin](https://vaadin.com/). Given the fact that this was the first time I
was exposed to a GWT-based web framework using Scala, I tried various coding
conventions, utility functions, shortcuts, etc. in the beginning. Over the
time, I came up with some common conventions that I employ throughout the code
base. In this post, I will share some of these custom tricks I developed along
this pursuit.

"Returning" the First Value
===========================

While creating a certain UI component, what a programmer occasionally performs
is to 1) instantiate the class, 2) set certain properties, and 3) return/use
the instance.

    #!scala
    val buttonLayout: HorizontalLayout = {
      val layout = new HorizontalLayout
      layout.setMargin(true)
      layout.setSpacing(true)
      layout.addComponent(submitButton)
      layout.addComponent(resetButton)
      layout
    }

This pattern was so idiomatic and repetitive throughout the code base that I
thought having something similar to [prog1 in Common
Lisp](http://www.lispworks.com/documentation/HyperSpec/Body/m_prog1c.htm)
would be really helpful for structuring similar components. Hence, I came up
with my own `returning` utility function as follows:

    #!scala
    def returning[T](result: T)(body: T => Unit): T = {
      body(result)
      result
    }

When we employ `returning` in `buttonLayout`, code translates as follows:

    #!scala
    val buttonLayout: HorizontalLayout =
      returning(new HorizontalLayout) {
        layout => 
          layout.setMargin(true)
          layout.setSpacing(true)
          layout.addComponent(submitButton)
          layout.addComponent(resetButton)
      }

I find this version more clear on intent.

Reading Nullable Text Fields
============================

While coding in Scala, I write my code as if there are no `null`s. And
whenever there is an external API that I need to communicate and has potential
to return `null`, I wrap it in an `Option`. This practice also applies to
`getValue` method of `TextField`s in Vaadin. Hence, I purposed a common
function to read from text fields:

    #!scala
    def getTrimmedValue(field: AbstractTextField): Option[String] =
      Option(field.getValue).filterNot(_.trim.isEmpty)

Note that `getTrimmedValue` treats input fields of redundant whitespace as a
`None`.

Grouping Component Getters/Setters
==================================

While creating forms, I was using the following scheme to implement fields one
by one:

    #!scala
    val nameField: TextField = new TextField
    
    def getNameFieldValue: Option[String] = getTrimmedValue(nameField)
    
    def resetNameFieldValue(): Unit = nameField.setValue(name.orNull)
    
    val surnameField: TextField = new TextField
    
    def getSurnameFieldValue: Option[String] = getTrimmedValue(surnameField)
    
    def resetSurameFieldValue(): Unit = surnameField.setValue(surname.orNull)
    
    // ...
    
    def reset(): Unit = {
    	resetNameFieldValue()
    	resetSurnameFieldValue()
    	// ...
    }

Per see, the namespace of the class gets polluted as you add more fields. That
is, in order to implement a form of 10 fields, you end up with at least
3x10=30 class variables/methods. In order to mitigate this problem, I wrote a
custom trait to group component accessors into a single field:

    #!scala
    trait CustomField[ComponentType <: Component, ValueType] {
    
      val component: ComponentType
    
      def value(): ValueType
    
      def reset(): Unit
    
    }

Using `CustomField`, the above code translates to this:

    #!scala
    val nameField: CustomField[TextField, String] = new CustomField[TextField, String] {
    	
      val component: TextField = new TextField
    
      def value(): ComponentHelpers.getTrimmedValue(component)
    
      def reset(): Unit = nameField.setValue(name.orNull)
    
    }
    
    val surnameField: CustomField[TextField, String] = new CustomField[TextField, String] {
    	
      val component: TextField = new TextField
    
      def value(): ComponentHelpers.getTrimmedValue(component)
    
      def reset(): Unit = surnameField.setValue(surname.orNull)
    
    }
    
    // ...
    
    val fields: Seq[CustomField[_ <: Component, _]] = Seq(
      nameField,
      surnameField,
      // ...
    )
    
    def reset(): Unit = fields.foreach(_.reset())

Confirmation Dialogs
====================

This one needs no introduction I guess. Here it is:

    #!scala
    def confirmationDialog(title: String, content: String, ok: () => Unit, cancel: () => Unit): Unit = {
      lazy val dialog: ConfirmationDialog = new ConfirmationDialog(
        title, content,
        new ClickButtonEventHandler {
          override def handleEvent(event: ClickEvent): Unit = {
            try { ok() }
            catch { case _: Throwable => dialog.close() }
          }
        },
        new ClickButtonEventHandler {
          override def handleEvent(event: ClickEvent): Unit = {
            try { cancel() }
            catch { case _: Throwable => dialog.close() }
          }
        })
      UI.getCurrent.addWindow(dialog)
    }

And you use it as follows:

    #!scala
    override def uploadFinished(event: FinishedEvent): Unit =
      confirmationDialog(
        "Deploy Shelf Plan",
        """You are about to populate tables using the provided shelf plan.<br/>
          |Do you want to proceed?""".stripMargin,
        ok, cancel)

"Escapeable" Window
===================

So you have a `Window`, that you want to be `closeable` using the `ESCAPE`
key. Fine, just extend from `EscapeableWindow`:

    #!scala
    trait EscapeableWindow { self: Window =>
    
      protected val escapeActionHandler: Handler = new Handler {
    
        override def handleAction(action: Action, sender: scala.Any, target: scala.Any): Unit =
          if (action.equals(EscapeableWindow.escapeAction))
            close()
    
        override def getActions(target: scala.Any, sender: scala.Any): Array[Action] =
          Array(EscapeableWindow.escapeAction)
    
      }
    
      setClosable(true)
      this.addActionHandler(escapeActionHandler)
    
    }
    
    object EscapeableWindow {
    
      val escapeAction = new ShortcutAction("ESCAPE", ShortcutAction.KeyCode.ESCAPE, null)
    
    }

Boolean Combo Box
=================

For plain boolean options, you can just simply go with a check box. But if you
have a nullable boolean field, you need a representation to encapsulate three
different states: 1) true, 2) false, and 3) null. For that purpose, I use a
combo box as follows:

    #!scala
    def createBooleanComboBox
    (id: String,
     caption: String,
     description: Option[String] = None,
     nullSelectionAllowed: Boolean = false): ComboBox =
      Commons.returning(new ComboBox(id, caption)) {
        field =>
          field.setNullSelectionAllowed(nullSelectionAllowed)
          description.foreach(field.setDescription)
          Seq(true, false).foreach(field.addItem)
      }

And below you can find a field that uses `createBooleanComboBox`:

    #!scala
    val outputMultiValueField: ComboBox =
      createBooleanComboBox(
        "outputMultiValue",
        "Output Multi-Value",
        nullSelectionAllowed = true)
