<div class="tinyeditor">
    <div class="tinyeditor-header" ng-hide="editMode">
	<div class="tinyeditor-control" title="Bold" style="background-position-y: -120px;" ng-click="execCommand('bold')"></div>
	<div class="tinyeditor-control" title="Italic" style="background-position-y: -150px;" ng-click="execCommand('italic')"></div>
	<div class="tinyeditor-control" title="Underline" style="background-position-y: -180px;" ng-click="execCommand('underline')"></div>
	<div class="tinyeditor-control" title="Strikethrough" style="background-position-y: -210px;" ng-click="execCommand('strikethrough')"></div>
	<div class="tinyeditor-divider"></div><div class="tinyeditor-control" title="Subscript" style="background-position-y: -240px;" ng-click="execCommand('subscript')"></div>
	<div class="tinyeditor-control" title="Superscript" style="background-position-y: -270px;" ng-click="execCommand('superscript')"></div>
	<div class="tinyeditor-divider"></div><div class="tinyeditor-control" title="Insert Ordered List" style="background-position-y: -300px;" ng-click="execCommand('insertorderedlist')"></div>
	<div class="tinyeditor-control" title="Insert Unordered List" style="background-position-y: -330px;" ng-click="execCommand('insertunorderedlist')"></div>
	<div class="tinyeditor-divider"></div><div class="tinyeditor-control" title="Outdent" style="background-position-y: -360px;" ng-click="execCommand('outdent')"></div>
	<div class="tinyeditor-control" title="Indent" style="background-position-y: -390px;" ng-click="execCommand('indent')"></div>
	<div class="tinyeditor-divider"></div><div class="tinyeditor-control" title="Left Align" style="background-position-y: -420px;" ng-click="execCommand('justifyleft')"></div>
	<div class="tinyeditor-control" title="Center Align" style="background-position-y: -450px;" ng-click="execCommand('justifycenter')"></div>
	<div class="tinyeditor-control" title="Right Align" style="background-position-y: -480px;" ng-click="execCommand('justifyright')"></div>
	<div class="tinyeditor-control" title="Block Justify" style="background-position-y: -510px;" ng-click="execCommand('justifyfull')"></div>
	<div class="tinyeditor-divider"></div><div class="tinyeditor-control" title="Remove Formatting" style="background-position-y: -720px;" ng-click="execCommand('removeformat')"></div>
	<div class="tinyeditor-divider"></div><div class="tinyeditor-control" title="Undo" style="background-position-y: -540px;" ng-click="execCommand('undo')"></div>
	<div class="tinyeditor-control" title="Redo" style="background-position-y: -570px;" ng-click="execCommand('redo')"></div></div>
    <div class="tinyeditor-header" ng-hide="editMode">
	<select class="tinyeditor-font" ng-model="font" ng-options="a as a for a in fonts"><option value="">Font</option></select>
	<select class="tinyeditor-size" ng-model="fontsize" ng-options="a as a for a in fontsizes"><option value="">...</option></select>
	<select class="tinyeditor-style" ng-model="textstyle" ng-options="s.key as s.name for s in styles"><option value="">Style</option></select>
	<div class="tinyeditor-divider"></div>
	<div class="tinyeditor-control" title="Font Color" style="background-position-y: -779px; position: relative;" ng-click="showFontColors = !showFontColors">
	    <colors-grid show="showFontColors" on-pick="setFontColor(color)"><colors-grid>
	</div>
	<div class="tinyeditor-control" title="Background Color" style="background-position-y: -808px; position: relative;" ng-click="showBgColors = !showBgColors">
	    <colors-grid show="showBgColors" on-pick="setBgColor(color)"><colors-grid>
	</div>
	<div class="tinyeditor-divider"></div>
	<div class="tinyeditor-control" title="Insert Image" style="background-position-y: -600px;" ng-click="insertImage()"></div>
	<div class="tinyeditor-control" title="Insert Horizontal Rule" style="background-position-y: -630px;" ng-click="execCommand('inserthorizontalrule')"></div>
	<div class="tinyeditor-control" title="Insert Hyperlink" style="background-position-y: -660px;" ng-click="insertLink()"></div>
	<div class="tinyeditor-control" title="Remove Hyperlink" style="background-position-y: -690px;" ng-click="execCommand('unlink')"></div>
	<div class="tinyeditor-divider"></div><div class="tinyeditor-control" title="Print" style="background-position-y: -750px;" ng-click="execCommand('print')"></div>
    </div>
    <div>
	<textarea data-placeholder-attr="" style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; resize: none; width: 100%; height: 300px;" ng-show="editMode" ng-model="content"></textarea>
	<iframe style="-webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; width: 100%; height: 300px;" ng-hide="editMode" wframe="" ng-model="content"></iframe>
    </div>
    <div class="tinyeditor-footer">
	<div ng-switch="editMode" ng-click="editMode = !editMode" class="toggle"><span ng-switch-when="true">wysiwyg</span><span ng-switch-default>source</span></div>
    </div>
</div>
