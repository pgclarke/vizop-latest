# -*- coding: utf-8 -*-
# Module ft_full_report: part of Vizop, (c) 2020 xSeriCon
# produces full export of a fault tree

# library modules
from __future__ import division # makes a/b yield exact, not truncated, result. Must be 1st import
import os, os.path, wx, platform # wx provides basic GUI functions

import core_classes, project_display, vizop_misc, info, utilities, faulttree, display_utilities
from project_display import EditPanelAspectItem
from display_utilities import UIWidgetItem

class FTFullExportViewport(faulttree.FTForDisplay):
	# defines a viewport that produces an export file containing a full depiction of a fault tree, and displays a
	# dialogue to get parameters from the user to control the export (e.g. which items to include, fonts, page settings)
	InternalName = 'FTFullExport' # unique per class, used in messaging
	HumanName = _('Fault Tree full export')
	PreferredKbdShortcut = 'E'
	NewPHAObjRequired = None # which datacore PHA object class this Viewport spawns on creation.
		# Should be None if the model shouldn't create a PHA object
	# VizopTalks message when a new FT is created. NB don't set Priority here, as it is overridden in DoNewViewportCommand()
	NewViewportVizopTalksArgs = {'Title': 'Fault tree full export',
		'MainText': 'Enter the settings you require, then click Go'}
	NewViewportVizopTalksTips = []
	InitialEditPanelMode = 'Widgets'
	MinZoom = 0.1 # min and max zoom factors allowed for this Viewport
	MaxZoom = 9.99

	class FTFullExportDialogueAspect(project_display.EditPanelAspectItem):

		def OnFilenameTextWidget(self, Event=None, WidgetObj=None):
			# get filename stub provided by user
			UserFilenameStub = self.FilenameText.Widget.GetValue().strip()
			# get all actual filenames to use, based on this stub
			ActualFilenames = GetFilenamesForMultipageExport(BasePath=UserFilenameStub,
				FileType=core_classes.ImageFileTypesSupported[self.FileTypeChoice.Widget.GetSelection()],
				PagesAcross=self.PageCountInfo['PagesAcrossCount'], PagesDown=self.PageCountInfo['PagesDownCount'])
			print('FR37 filenames to use: ', ActualFilenames)
			# update filename status text, Go button status etc
			FilenameStatus = self.UpdateWidgetStatus()
			# write name back into widget, if filename is usable
			if FilenameStatus not in ['CannotWrite', 'NoAccess', 'Other']:
				self.FilenameText.Widget.ChangeValue(UserFilenameStub)

		def OnSelectButton(self, Event):
			# fetch any filename already provided in the file stub textctrl
			UserFilenameStub = self.FilenameText.Widget.GetValue().strip()
			if UserFilenameStub: # if user has entered a filename, provide it as default
				DefaultBasename = os.path.basename(UserFilenameStub)
			else:
				# get last used export filename from project%%%
				DefaultBasename = self.Proj.FTFullExportFilename
			# get the wildcard to use in the filename dialogue box
			DefaultExtension = core_classes.ImageFileTypesSupported[self.FileTypeChoice.Widget.GetSelection()].Extension
			Wildcard = '*' + os.extsep + DefaultExtension
			# get default directory = directory in filename textctrl, last export save directory or project save directory, if any
			if os.path.exists(os.path.dirname(UserFilenameStub)): DefaultDirectory = os.path.dirname(UserFilenameStub)
			elif os.path.exists(os.path.dirname(self.Proj.FTFullExportFilename)):
				DefaultDirectory = os.path.dirname(self.Proj.FTFullExportFilename)
			elif os.path.exists(os.path.dirname(self.Proj.OutputFilename)): DefaultDirectory = os.path.dirname(self.Proj.OutputFilename)
			else: DefaultDirectory = info.DefaultUserDirectory
			(GetFilenameSuccess, SaveFilename) = vizop_misc.GetFilenameForSave(self.TopLevelFrame,
				DialogueTitle=_('Select filename stub for FT export'), DefaultDir=DefaultDirectory,
				DefaultFile=DefaultBasename, Wildcard=Wildcard, DefaultExtension=DefaultExtension)
			if GetFilenameSuccess:
				# write pathname into filename textctrl
				self.FilenameText.Widget.ChangeValue(SaveFilename)
				# update filename status text, Go button status etc
				FilenameStatus = self.UpdateWidgetStatus()

		def OnFileTypeChoice(self, Event): # handle user selection of file type
			# update the file extension in the file name textctrl, if any
			# first, check if the existing filename has an extension matching any valid image file type
			OldFilePath = self.FilenameText.Widget.GetValue().strip()
			OldExtension = os.path.splitext(OldFilePath)[1]
			if OldExtension in [(os.extsep + t.Extension) for t in core_classes.ImageFileTypesSupported]:
				# remove old extension and separator behind (e.g. "MyFile.pdf" -> "MyFile")
				NewFilePath = OldFilePath[:-len(OldExtension)]
			else: NewFilePath = OldFilePath
			# append separator, if filename doesn't already end in separator
			if not NewFilePath.endswith(os.extsep): NewFilePath += os.extsep
			# append new extension
			NewFilePath += core_classes.ImageFileTypesSupported[self.FileTypeChoice.Widget.GetSelection()].Extension
			# write new path back to file name textctrl
			self.FilenameText.Widget.ChangeValue(NewFilePath)
			self.FilenameText.Widget.SelectAll()

		def OnOverwriteCheck(self, Event): # handle click on Overwrite checkbox: store overwrite option
			self.Overwrite = self.OverwriteCheck.Widget.GetValue()
			# update filename status text, Go button status etc
			FilenameStatus = self.UpdateWidgetStatus()

		def OnShowHeaderCheck(self, Event): pass
		def OnShowFTCheck(self, Event): pass
		def OnShowSelectedCheck(self, Event): pass
		def OnPageSizeChoice(self, Event): pass
		def OnPortraitRadio(self, Event): pass
		def OnLandscapeRadio(self, Event): pass
		def OnMarginTextCtrl(self, Event=None, WidgetObj=None): pass # need to write legal value into self.Margins{}
		def OnPageNumberTopRadio(self, Event): pass
		def OnPageNumberBottomRadio(self, Event): pass
		def OnPageNumberNoneRadio(self, Event): pass
		def OnPageNumberLeftRadio(self, Event): pass
		def OnPageNumberCentreRadio(self, Event): pass
		def OnPageNumberRightRadio(self, Event): pass
		def OnPagesAcrossTextCtrl(self, Event=None, WidgetObj=None): pass
		def OnPagesDownTextCtrl(self, Event=None, WidgetObj=None): pass
		def OnNewPagePerRRCheck(self, Event): pass
		def OnZoomTextCtrl(self, Event=None, WidgetObj=None): pass # need to write legal value to self.Zoom
		def OnBlackWhiteCheck(self, Event): pass
		def OnFontChoice(self, Event): pass
		def OnConnectorsAcrossPagesCheck(self, Event): pass
		def OnCommentsCheck(self, Event): pass
		def OnActionsCheck(self, Event): pass
		def OnParkingCheck(self, Event): pass
		def OnCannotCalculateTextCtrl(self, Event=None, WidgetObj=None): pass
		def OnCombineRRsCheck(self, Event): pass
		def OnExpandGatesCheck(self, Event): pass
		def OnDateChoice(self, Event): pass
		def OnCancelButton(self, Event): pass

		def OnGoButton(self, Event): # %%%
			# get string containing information about export required
			ShowWhat, PageNumberWhere, ShowTexts = self.MakeAttribStrings()
			ExportInput = {'FilePath': self.FilenameText.Widget.GetValue().strip(),
				'FileType': core_classes.ImageFileTypesSupported[self.FileTypeChoice.Widget.GetSelection()],
				'Zoom': self.Zoom, 'ShowWhat': ShowWhat,
				'PageSizeLongAxis': core_classes.PaperSizes[self.PageSizeChoice.Widget.GetSelection()].SizeLongAxis,
				'PageSizeShortAxis': core_classes.PaperSizes[self.PageSizeChoice.Widget.GetSelection()].SizeShortAxis,
				'Orientation': 'Portrait' if self.PortraitRadio.Widget.GetValue() else 'Landscape',
				'TopMargin': self.Margins['ExportPaperTopMargin'],
				'BottomMargin': self.Margins['ExportPaperBottomMargin'],
				'LeftMargin': self.Margins['ExportPaperLeftMargin'], 'RightMargin': self.Margins['ExportPaperRightMargin'],
				'PageNumberPos': PageNumberWhere, 'FirstPageNumber': 1, 'PageCountToShow': 'Auto',
				'NewPagePerRR': self.NewPagePerRRCheck.Widget.IsChecked(),
				'Font': self.ParentFrame.TopLevelFrame.SystemFontNames[self.FontChoice.Widget.GetSelection()],
				'ConnectorsAcrossPages': self.ConnectorsAcrossPagesCheck.Widget.IsChecked(),
				'ShowTexts': ShowTexts,
				'CannotCalculateText': self.CannotCalculateText.Widget.GetValue().strip(),
				'CombineRRs': self.CombineRRsCheck.Widget.IsChecked(),
				'ExpandGates': self.ExpandGatesCheck.Widget.IsChecked(),
				'DateKind': core_classes.DateChoices[self.DateChoice.Widget.GetSelection()] }
			self.FT.DoExportFTToFile(**ExportInput)
			self.StoreAttribsInProject()

		def MakeAttribStrings(self):
			# return ShowWhat, PageNumberWhere and ShowTexts (3 x str) containing information about export required
#			ThisAspect = self.DisplDevice.MyEditPanel.FTFullExportAspect # needed instead of self?
			# make string containing labels of parts of FT to be exported, e.g. 'Header,FT'
			ShowWhat = ','.join([w.XMLLabel for w in [self.ShowHeaderCheck, self.ShowFTCheck,
				self.ShowOnlySelectedCheck] if w.Widget.IsChecked()])
			# make string containing labels of page number positions, e.g. 'Top,Left'
			PageNumberWhere = ','.join([w.XMLLabel for w in [self.PageNumberBottomRadio, self.PageNumberCentreRadio,
				self.PageNumberLeftRadio, self.PageNumberRightRadio, self.PageNumberTopRadio,
				self.PageNumberNoneRadio] if w.Widget.GetValue()])
			# make string containing labels of texts to be exported, e.g. 'Action,Parking'
			ShowTexts = ','.join([w.XMLLabel for w in [self.CommentsCheck, self.ActionsCheck,
				self.ParkingCheck] if w.Widget.IsChecked()])
			return ShowWhat, PageNumberWhere, ShowTexts

		def StoreAttribsInProject(self):
			# send request to datacore to store parameters in project
#			ThisAspect = self.DisplDevice.MyEditPanel.FTFullExportAspect
			ThisViewport = self.ParentFrame.TopLevelFrame.CurrentViewport
			# gets string containing information about export required
			ShowWhat, PageNumberWhere, ShowTexts = self.MakeAttribStrings()
			vizop_misc.SendRequest(Socket=ThisViewport.C2DSocketREQ,
				Command='RQ_FT_UpdateFullExportAttribs',
				Proj=self.Proj.ID, PHAObj=ThisViewport.PHAObj.ID, Viewport=ThisViewport.ID,
				Filename=self.FilenameText.Widget.GetValue().strip(),
				FileType=core_classes.ImageFileTypesSupported[self.FileTypeChoice.Widget.GetSelection()].XMLName,
				ExportWhat=ShowWhat,
				PageSize=core_classes.PaperSizes[self.PageSizeChoice.Widget.GetSelection()].XMLName,
				PaperOrientation='Portrait' if self.PortraitRadio.Widget.GetValue() else 'Landscape',
				MarginLeft=str(self.Margins['ExportPaperLeftMargin']), MarginRight=str(self.Margins['ExportPaperRightMargin']),
				MarginTop=str(self.Margins['ExportPaperTopMargin']), MarginBottom=str(self.Margins['ExportPaperBottomMargin']),
				PageNumberLoc=PageNumberWhere,
				Zoom=str(self.Zoom),
				NewPagePerRR=utilities.Bool2Str(self.NewPagePerRRCheck.Widget.IsChecked()),
				Monochrome=utilities.Bool2Str(self.BlackWhiteCheck.Widget.IsChecked()),
				Font=self.ParentFrame.TopLevelFrame.SystemFontNames[self.FontChoice.Widget.GetSelection()],
				ConnectorsAcrossPageBreaks=utilities.Bool2Str(self.ConnectorsAcrossPagesCheck.Widget.IsChecked()),
				IncludeWhatTexts=ShowTexts,
				CannotCalculateText=self.CannotCalculateText.Widget.GetValue().strip(),
				CombineRRs=utilities.Bool2Str(self.CombineRRsCheck.Widget.IsChecked()),
				ExpandGates=utilities.Bool2Str(self.ExpandGatesCheck.Widget.IsChecked()),
				DateToShow=core_classes.DateChoices[self.DateChoice.Widget.GetSelection()].XMLName)

		def Prefill(self, Proj, FT, SystemFontNames):
			# prefill widget values
			self.Proj = Proj # used in widget handlers
			self.FT = FT # used in widget handlers
			# filename is fetched from last used filename in the project
			self.FilenameText.Widget.ChangeValue(Proj.FTFullExportFilename.strip())
			self.FilenameText.Widget.SelectAll()
			# file type is fetched from project
			RecognisedExtensions = [t.Extension for t in core_classes.ImageFileTypesSupported]
			if Proj.FTFullExportFileType in RecognisedExtensions: ExtensionToSelect = Proj.FTFullExportFileType
			else: ExtensionToSelect = info.DefaultImageFileType
			self.FileTypeChoice.Widget.SetSelection(RecognisedExtensions.index(ExtensionToSelect))
			# set overwrite checkbox
			self.OverwriteCheck.Widget.SetValue(self.Overwrite)
#			# set filename status message
#			self.UpdateFilenameStatusMessage()
			# set scope checkboxes
			self.ShowHeaderCheck.Widget.SetValue('Header' in Proj.FTExportShowWhat)
			self.ShowFTCheck.Widget.SetValue('FT' in Proj.FTExportShowWhat)
			self.ShowOnlySelectedCheck.Widget.SetValue('OnlySelected' in Proj.FTExportShowWhat)
			# set layout widget values
			# get user's preferred paper size from config file
			PaperSizeStr = vizop_misc.GetValueFromUserConfig('ExportPaperSize')
			if PaperSizeStr == '': PaperSizeStr = info.DefaultPaperSize
			PaperSizesStr = [p.HumanName for p in core_classes.PaperSizes]
			# use 0th paper size if preferred paper size isn't in list of available paper sizes
			TargetPaperSizeIndex = PaperSizesStr.index(PaperSizeStr) if PaperSizeStr in PaperSizesStr else 0
			TargetPaperSize = core_classes.PaperSizes[TargetPaperSizeIndex]
			self.PageSizeChoice.Widget.SetSelection(TargetPaperSizeIndex)
			# set landscape or portrait
			PaperOrientation = vizop_misc.GetValueFromUserConfig('ExportPaperOrientation')
			if PaperOrientation == '': PaperOrientation = info.DefaultPaperOrientation
			if PaperOrientation == 'Portrait': self.PortraitRadio.Widget.SetValue(True)
			elif PaperOrientation == 'Landscape': self.LandscapeRadio.Widget.SetValue(True)
			# set paper margin text boxes
			self.Margins = {} # store margin values
			for ThisWidget, ConfigName, Default in [
					(self.TopMarginText, 'ExportPaperTopMargin', info.DefaultPaperTopMargin),
					(self.BottomMarginText, 'ExportPaperBottomMargin', info.DefaultPaperBottomMargin),
					(self.LeftMarginText, 'ExportPaperLeftMargin', info.DefaultPaperLeftMargin),
					(self.RightMarginText, 'ExportPaperRightMargin', info.DefaultPaperRightMargin) ]:
#				ThisMarginStr = vizop_misc.GetValueFromUserConfig(ConfigName)
				# converting to string, then back to real, to avoid problems with bad values in user-edited project file
				ThisMarginStr = str(Proj.ExportPaperMargins.get(ConfigName, Default))
				if ThisMarginStr == '': ThisMarginStr = Default
				self.Margins[ConfigName] = utilities.str2real(ThisMarginStr, meaninglessvalue=12) # used for function call later
				ThisWidget.Widget.ChangeValue(ThisMarginStr.strip())
			# set page number location radio buttons. Expected PageNumberPos is e.g. 'Top,Left'
#			PageNumberPos = vizop_misc.GetValueFromUserConfig('ExportPageNumberPos')
			PageNumberPos = Proj.ExportPageNumberLoc
			if PageNumberPos == '': PageNumberPos = info.DefaultPaperPageNumberPos
			for ThisWidget, Pos in [ (self.PageNumberTopRadio, 'Top'), (self.PageNumberBottomRadio, 'Bottom'),
					(self.PageNumberLeftRadio, 'Left'), (self.PageNumberRightRadio, 'Right'),
					(self.PageNumberNoneRadio, 'None'), (self.PageNumberCentreRadio, 'Centre') ]:
				ThisWidget.Widget.SetValue(Pos in PageNumberPos)
			# set black-and-white checkbox
			self.BlackWhiteCheck.Widget.SetValue(Proj.LastExportBlackAndWhite)
			# set font choice box; first choice is last font used in this project, then last font used by this user
			PreferredFontName = Proj.LastExportFontName
			if PreferredFontName in SystemFontNames: FontNameToUse = PreferredFontName
			else:
				LastUserFontName = vizop_misc.GetValueFromUserConfig('ExportFontName')
				if LastUserFontName in SystemFontNames: FontNameToUse = LastUserFontName
				# if last font name not found, select the first system font name, if any
				elif SystemFontNames: FontNameToUse = SystemFontNames[0]
				else: FontNameToUse = ''
			if FontNameToUse: self.FontChoice.Widget.SetSelection(SystemFontNames.index(FontNameToUse))
			# set depiction checkboxes
			self.ConnectorsAcrossPagesCheck.Widget.SetValue(Proj.FTConnectorsAcrossPages)
			ShowComments = 'Comments' in Proj.FTExportShowPeripheral
			ShowActions = 'Actions' in Proj.FTExportShowPeripheral
			ShowParking = 'Parking' in Proj.FTExportShowPeripheral
			self.CommentsCheck.Widget.SetValue(ShowComments)
			self.ActionsCheck.Widget.SetValue(ShowActions)
			self.ParkingCheck.Widget.SetValue(ShowParking)
			self.CannotCalculateText.Widget.SetValue(Proj.FTExportCannotCalculateText)
			self.CombineRRsCheck.Widget.SetValue(Proj.FTExportCombineRRs)
			self.ExpandGatesCheck.Widget.SetValue(Proj.FTExportExpandGates)
			# set date choice box
			DateChoicesInternalNames = [d.XMLName for d in core_classes.DateChoices]
			PreferredDateToShow = Proj.LastExportPreferredDateToShow
			if PreferredDateToShow in core_classes.DateChoices: DateToShow = PreferredDateToShow
			else:
				LastUserDateToShow = vizop_misc.GetValueFromUserConfig('ExportDateToShow')
				if LastUserDateToShow in DateChoicesInternalNames: DateToShow = LastUserDateToShow
				# if last date kind not found, select the date kind flagged as 'Default'
				else: DateToShow = core_classes.DateChoices[
					[getattr(d, 'Default', False) for d in core_classes.DateChoices].index(True)]
			self.DateChoice.Widget.SetSelection(core_classes.DateChoices.index(DateToShow))
			# set NewPagePerRRCheck
			self.NewPagePerRRCheck.Widget.SetValue(Proj.FTExportNewPagePerRR)
			# set zoom and pages across/down value widgets. Zoom value is the last value used in this project;
			# Pages across/down is the required number at this zoom level
			self.Zoom = Proj.FTFullExportZoom
			self.ZoomText.Widget.ChangeValue(str(self.Zoom * 100))
			self.ZoomText.Widget.SelectAll()
			PageCountInput = {'FT': FT, 'Zoom': self.Zoom, 'ShowWhat': Proj.FTExportShowWhat,
				'PageSizeLongAxis': TargetPaperSize.SizeLongAxis, 'PageSizeShortAxis': TargetPaperSize.SizeShortAxis,
				'Orientation': PaperOrientation, 'TopMargin': self.Margins['ExportPaperTopMargin'],
				'BottomMargin': self.Margins['ExportPaperBottomMargin'],
				'LeftMargin': self.Margins['ExportPaperLeftMargin'], 'RightMargin': self.Margins['ExportPaperRightMargin'],
				'PageNumberPos': PageNumberPos, 'FirstPageNumber': 1, 'PageCountToShow': 'Auto',
				'NewPagePerRR': Proj.FTExportNewPagePerRR, 'Font': FontNameToUse,
				'ConnectorsAcrossPages': Proj.FTConnectorsAcrossPages,
				'ShowComments': ShowComments, 'ShowActions': ShowActions, 'ShowParking': ShowParking,
				'CannotCalculateText': Proj.FTExportCannotCalculateText, 'CombineRRs': Proj.FTExportCombineRRs,
				'ExpandGates': Proj.FTExportExpandGates, 'DateKind': DateToShow }
			self.PageCountInfo = FT.GetPageCountInfo(**PageCountInput)
			self.PagesAcrossText.Widget.ChangeValue(str(self.PageCountInfo['PagesAcrossCount']))
			self.PagesAcrossText.Widget.SelectAll()
			self.PagesDownText.Widget.ChangeValue(str(self.PageCountInfo['PagesDownCount']))
			self.PagesDownText.Widget.SelectAll()
			self.UpdateWidgetStatus()

		def UpdateFilenameStatusMessage(self, UserFilePath='', ActualFilePathsToUse=[]):
			# update filename status message widget text based UserFilePath (str; what's currently in the Filename
			# text box) and ActualFilePathsToUse (list; all file paths to use for multipage export)
			# return FilenameStatus (str)
			assert isinstance(UserFilePath, str)
			# check status of each item in ActualFilePathsToUse, if any
			PathStati = []
			for ThisPath in ActualFilePathsToUse:
				# is the path a writeable path with no existing file?
				if vizop_misc.IsWriteableAsNewFile(ThisPath): ThisPathStatus = 'CanWrite'
				# is the path a writeable path, with an existing file?
				elif os.path.isfile(ThisPath) and os.access(ThisPath, os.W_OK): ThisPathStatus = 'NeedToOverwrite'
				# is the path unusable?
				else: ThisPathStatus = 'CannotWrite'
				PathStati.append(ThisPathStatus)
			# 1. Filename text box empty, or whitespace only, or contains a directory path
			if (not UserFilePath) or os.path.isdir(UserFilePath):
				Message = _('Please provide a filename for the export')
				FilenameStatus = 'NotFilename'
			# 2. Paths to use are all writeable, nonexistent filenames
			elif PathStati.count('CanWrite') == len(PathStati):
				if len(ActualFilePathsToUse) == 1: Message = _('Ready to export to 1 new file. Click Go')
				else: Message = _('Ready to export to %d new files. Click Go') % len(ActualFilePathsToUse)
				FilenameStatus = 'ReadyToMakeNewFile'
			# 3. Paths point to at least 1 existent file that can be overwritten, and Overwrite check box is checked
			elif (PathStati.count('NeedToOverwrite') > 0) and ('CannotWrite' not in PathStati)  and \
					self.OverwriteCheck.Widget.GetValue():
				Message = _('Ready to export. Existing file(s) will be overwritten when you click Go')
				FilenameStatus = 'ReadyToOverwrite'
			# 4. Path points to an existent file that can be overwritten, and Overwrite check box is unchecked
			elif (PathStati.count('NeedToOverwrite') > 0) and ('CannotWrite' not in PathStati) and \
					not self.OverwriteCheck.Widget.GetValue():
				if len(ActualFilePathsToUse) == 1: Message = _('File exists. Click "Overwrite", then "Go"')
				else: Message = _('One or more files already exist. Click "Overwrite", then "Go"')
				FilenameStatus = 'FileExists'
			# 5. Path points to a writeable folder, but no extension is provided and it is needed (i.e. Windows)
			elif vizop_misc.IsWritableLocation(UserFilePath) and os.path.splitext(UserFilePath)[1] in ['', '.'] \
					and platform.system() == 'Windows':
				Message = _('Please provide a valid file extension, e.g. .pdf')
				FilenameStatus = 'NeedExtension'
			# 6. Path points to a nonexistent folder, or a folder with no write access
			elif not vizop_misc.IsWritableLocation(UserFilePath):
				Message = _("%s can't write to that location") % info.PROG_SHORT_NAME
				FilenameStatus = 'NoAccess'
			# 99. Some other case we haven't thought of
			else:
				Message = _('You should buy a lottery ticket today')
				FilenameStatus = 'Other'
			self.FilenameStatusMessage.Widget.SetLabel(Message)
			return FilenameStatus

		def SetWidgetVisibility(self, **Args):
			# set IsVisible attribs for all fixed and variable widgets
			for ThisWidget in self.WidgetList: ThisWidget.IsVisible = True

		def UpdateWidgetStatus(self):
			# update enabled/disabled status of all widgets
			# First, get a list of all actual filenames to use for multipage export
			UserFilenameStub = self.FilenameText.Widget.GetValue().strip()
			ActualFilenames = GetFilenamesForMultipageExport(BasePath=UserFilenameStub,
				FileType=core_classes.ImageFileTypesSupported[self.FileTypeChoice.Widget.GetSelection()],
				PagesAcross=self.PageCountInfo['PagesAcrossCount'], PagesDown=self.PageCountInfo['PagesDownCount'])
			FilenameStatus = self.UpdateFilenameStatusMessage(UserFilePath=UserFilenameStub,
				ActualFilePathsToUse=ActualFilenames)
			# set status of Go button
			self.GoButton.Widget.Enable(FilenameStatus in ['ReadyToMakeNewFile', 'ReadyToOverwrite'])
			return FilenameStatus


		def __init__(self, InternalName, ParentFrame, TopLevelFrame):
			project_display.EditPanelAspectItem.__init__(self, WidgetList=[], InternalName=InternalName,
				ParentFrame=ParentFrame, TopLevelFrame=TopLevelFrame, PrefillMethod=self.Prefill,
				SetWidgetVisibilityMethod=self.SetWidgetVisibility)
			self.Overwrite = False # whether to overwrite any existing file when exporting

	def MakeFTFullExportAspect(self, MyEditPanel, Fonts, SystemFontNames, DateChoices):
		# make Control Panel aspect for PHAModel control
		# fonts (dict): internal font objects such as SmallHeadingFont
		# SystemFontNames (list of str): names of "real" fonts available on the platform
		# DateChoices (list of ChoiceItem): options for date to show in FT
		# return the aspect
		# make basic attribs needed for the aspect
		MyEditPanel.FTFullExportAspect = FTFullExportViewport.FTFullExportDialogueAspect(InternalName='FTFullExport',
			ParentFrame=MyEditPanel, TopLevelFrame=MyEditPanel.TopLevelFrame)
		ThisAspect = MyEditPanel.FTFullExportAspect
		ThisAspect.TextWidgets = []
		# make box sizers to contain groups of widgets
		FileBoxSizer = wx.StaticBoxSizer(orient=wx.VERTICAL, parent=MyEditPanel, label=_('About the file to export'))
		FileBoxSubSizer = wx.GridBagSizer(hgap=5, vgap=5)
		FileBoxSizer.Add(FileBoxSubSizer)
		ScopeBoxSizer = wx.StaticBoxSizer(orient=wx.VERTICAL, parent=MyEditPanel, label=_('What to include in the export'))
		ScopeBoxSubSizer = wx.GridBagSizer(hgap=5, vgap=5)
		ScopeBoxSizer.Add(ScopeBoxSubSizer)
		PageLayoutBoxSizer = wx.StaticBoxSizer(orient=wx.VERTICAL, parent=MyEditPanel, label=_('Page layout'))
		PageLayoutBoxSubSizer = wx.GridBagSizer(hgap=5, vgap=5)
		PageLayoutBoxSizer.Add(PageLayoutBoxSubSizer)
		StyleBoxSizer = wx.StaticBoxSizer(orient=wx.VERTICAL, parent=MyEditPanel, label=_('Fault Tree style'))
		StyleBoxSubSizer = wx.GridBagSizer(hgap=5, vgap=5)
		StyleBoxSizer.Add(StyleBoxSubSizer)
		ActionBoxSizer = wx.StaticBoxSizer(orient=wx.VERTICAL, parent=MyEditPanel, label=' ')
		ActionBoxSubSizer = wx.GridBagSizer(hgap=5, vgap=5)
		ActionBoxSizer.Add(ActionBoxSubSizer)
		# make header widget
		ThisAspect.HeaderLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1,
			_('Export full Fault Tree report')),
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, GapY=10,
			ColLoc=0, ColSpan=10, Font=Fonts['BigHeadingFont'], NewRow=True)
		ThisAspect.FileBox = UIWidgetItem(FileBoxSizer, HideMethod=lambda : FileBoxSizer.ShowItems(False),
			ShowMethod=lambda : FileBoxSizer.ShowItems(True), ColLoc=0, ColSpan=5, NewRow=True,
			SetFontMethod=lambda f: FileBoxSizer.GetStaticBox().SetFont, Font=Fonts['SmallHeadingFont'])
		ThisAspect.FilenameLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Filename stub:'),
			style=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
			ColLoc=0, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.FilenameText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER),
			MinSizeY=25, Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnFilenameTextWidget, GapX=5,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND,
			MinSizeX=300, ColLoc=2, ColSpan=1, DisplayMethod='StaticFromText')
		ThisAspect.SelectButton = UIWidgetItem(wx.Button(MyEditPanel, -1, _('Select')),
			Handler=ThisAspect.OnSelectButton, Events=[wx.EVT_BUTTON], ColLoc=3, ColSpan=1,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND)
		ThisAspect.FileTypeLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Type:')),
			ColLoc=4, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.FileTypeChoice = UIWidgetItem(wx.Choice(MyEditPanel, -1, size=(70, 25),
			choices=[t.HumanName for t in core_classes.ImageFileTypesSupported]),
			Handler=ThisAspect.OnFileTypeChoice, Events=[wx.EVT_CHOICE], ColLoc=5, ColSpan=1)
		ThisAspect.OverwriteCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Overwrite')),
			Handler=ThisAspect.OnOverwriteCheck, Events=[wx.EVT_CHECKBOX], ColLoc=2, ColSpan=1, NewRow=True)
		ThisAspect.FilenameStatusMessage = UIWidgetItem(wx.StaticText(MyEditPanel, -1, ''),
			ColLoc=2, ColSpan=3, Font=Fonts['BoldFont'], NewRow=True)
		# add widgets to FileBoxSubSizer, and populate list of text widgets
		ThisAspect.TextWidgets.extend(display_utilities.PopulateSizer(Sizer=FileBoxSubSizer, Widgets=[ThisAspect.FilenameLabel,
			ThisAspect.FilenameText, ThisAspect.SelectButton, ThisAspect.FileTypeLabel, ThisAspect.FileTypeChoice,
			ThisAspect.OverwriteCheck, ThisAspect.FilenameStatusMessage]))
		# widgets in "scope" box
		ThisAspect.ScopeBox = UIWidgetItem(ScopeBoxSizer, HideMethod=lambda : ScopeBoxSizer.ShowItems(False),
			ShowMethod=lambda : ScopeBoxSizer.ShowItems(True), ColLoc=0, ColSpan=5, NewRow=True,
			SetFontMethod=lambda f: ScopeBoxSizer.GetStaticBox().SetFont, Font=Fonts['SmallHeadingFont'])
		ThisAspect.ExportWhatLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Export what:')),
			ColLoc=0, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.ShowHeaderCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Header block')),
			Handler=ThisAspect.OnShowHeaderCheck, Events=[wx.EVT_CHECKBOX], ColLoc=1, ColSpan=1, XMLLabel='Header')
		ThisAspect.ShowFTCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Fault tree')),
			Handler=ThisAspect.OnShowFTCheck, Events=[wx.EVT_CHECKBOX], ColLoc=2, ColSpan=1, XMLLabel='FT')
		ThisAspect.ShowOnlySelectedCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Selected elements only')),
			Handler=ThisAspect.OnShowSelectedCheck, Events=[wx.EVT_CHECKBOX], ColLoc=3, ColSpan=1, XMLLabel='OnlySelected')
		ThisAspect.IncludeWhatLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Include:')), NewRow=True,
			ColLoc=0, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.CommentsCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Comments')),
			Handler=ThisAspect.OnCommentsCheck, Events=[wx.EVT_CHECKBOX], ColLoc=1, ColSpan=1, XMLLabel='Comments')
		ThisAspect.ActionsCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Action items')),
			Handler=ThisAspect.OnActionsCheck, Events=[wx.EVT_CHECKBOX], ColLoc=2, ColSpan=1, XMLLabel='ActionItems')
		ThisAspect.ParkingCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Parking lot items')),
			Handler=ThisAspect.OnParkingCheck, Events=[wx.EVT_CHECKBOX], ColLoc=3, ColSpan=1, XMLLabel='ParkingLotItems')
		# add widgets to FileBoxSubSizer
		ThisAspect.TextWidgets.extend(display_utilities.PopulateSizer(Sizer=ScopeBoxSubSizer, Widgets=[ThisAspect.ExportWhatLabel,
			ThisAspect.ShowHeaderCheck, ThisAspect.ShowFTCheck, ThisAspect.ShowOnlySelectedCheck,
			ThisAspect.IncludeWhatLabel, ThisAspect.CommentsCheck, ThisAspect.ActionsCheck, ThisAspect.ParkingCheck]))
		# widgets in "page layout" box
		ThisAspect.PageLayoutBox = UIWidgetItem(PageLayoutBoxSizer, HideMethod=lambda : PageLayoutBoxSizer.ShowItems(False),
			ShowMethod=lambda : PageLayoutBoxSizer.ShowItems(True), ColLoc=5, ColSpan=5, RowSpan=2,
			SetFontMethod=lambda f: PageLayoutBoxSizer.GetStaticBox().SetFont, Font=Fonts['SmallHeadingFont'])
#		ThisAspect.PageLayoutLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1,
#			_('Page layout')),
#			ColLoc=0, ColSpan=2, Font=Fonts['SmallHeadingFont'])
		ThisAspect.PageSizeLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Page size:')),
			ColLoc=0, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.PageSizeChoice = UIWidgetItem(wx.Choice(MyEditPanel, -1, size=(200, 25),
			choices=[t.FullNameForDisplay for t in core_classes.PaperSizes]),
			Handler=ThisAspect.OnPageSizeChoice, Events=[wx.EVT_CHOICE], ColLoc=1, ColSpan=3)
		ThisAspect.PortraitRadio = UIWidgetItem(wx.RadioButton(MyEditPanel, -1, _('Portrait'), style=wx.RB_GROUP),
			Handler=ThisAspect.OnPortraitRadio, Events=[wx.EVT_RADIOBUTTON], ColLoc=4)
		ThisAspect.LandscapeRadio = UIWidgetItem(wx.RadioButton(MyEditPanel, -1, _('Landscape')),
			Handler=ThisAspect.OnLandscapeRadio, Events=[wx.EVT_RADIOBUTTON], ColLoc=5)
		ThisAspect.MarginLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Margins (mm):')),
			ColLoc=0, ColSpan=1, NewRow=True, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.TopMarginLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Top')),
			ColLoc=1, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.TopMarginText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER), MinSizeY=25,
			Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnMarginTextCtrl,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, MinSizeX=100, ColLoc=2, ColSpan=1,
			DisplayMethod='StaticFromText')
		ThisAspect.BottomMarginLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Bottom')),
			ColLoc=1, ColSpan=1, NewRow=True, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.BottomMarginText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER), MinSizeY=25,
			Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnMarginTextCtrl,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, MinSizeX=100, ColLoc=2, ColSpan=1,
			DisplayMethod='StaticFromText')
		ThisAspect.LeftMarginLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Left')),
			ColLoc=1, ColSpan=1, NewRow=True, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.LeftMarginText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER), MinSizeY=25,
			Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnMarginTextCtrl,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, MinSizeX=100, ColLoc=2, ColSpan=1,
			DisplayMethod='StaticFromText')
		ThisAspect.RightMarginLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Right')),
			ColLoc=1, ColSpan=1, NewRow=True, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.RightMarginText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER), MinSizeY=25,
			Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnMarginTextCtrl,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, MinSizeX=100, ColLoc=2, ColSpan=1,
			DisplayMethod='StaticFromText')
		ThisAspect.PageNumberingLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Page numbers\nat:'),
			style=wx.ALIGN_RIGHT), ColLoc=3, ColSpan=1, RowSpan=2)
		ThisAspect.PageNumberTopRadio = UIWidgetItem(wx.RadioButton(MyEditPanel, -1, _('Top'), style=wx.RB_GROUP),
			Handler=ThisAspect.OnPageNumberTopRadio, Events=[wx.EVT_RADIOBUTTON], ColLoc=4, XMLLabel='Top')
		ThisAspect.PageNumberBottomRadio = UIWidgetItem(wx.RadioButton(MyEditPanel, -1, _('Bottom')), XMLLabel='Bottom',
			Handler=ThisAspect.OnPageNumberBottomRadio, Events=[wx.EVT_RADIOBUTTON], ColLoc=4)
		ThisAspect.PageNumberNoneRadio = UIWidgetItem(wx.RadioButton(MyEditPanel, -1, _('None')), XMLLabel='None',
			Handler=ThisAspect.OnPageNumberNoneRadio, Events=[wx.EVT_RADIOBUTTON], ColLoc=4)
		ThisAspect.PageNumberLeftRadio = UIWidgetItem(wx.RadioButton(MyEditPanel, -1, _('Left'), style=wx.RB_GROUP),
			Handler=ThisAspect.OnPageNumberLeftRadio, Events=[wx.EVT_RADIOBUTTON], ColLoc=5, XMLLabel='Left')
		ThisAspect.PageNumberCentreRadio = UIWidgetItem(wx.RadioButton(MyEditPanel, -1, _('Centre')), XMLLabel='Centre',
			Handler=ThisAspect.OnPageNumberCentreRadio, Events=[wx.EVT_RADIOBUTTON], ColLoc=5)
		ThisAspect.PageNumberRightRadio = UIWidgetItem(wx.RadioButton(MyEditPanel, -1, _('Right')), GapY=10,
			Handler=ThisAspect.OnPageNumberRightRadio, Events=[wx.EVT_RADIOBUTTON], ColLoc=5,  XMLLabel='Right')
		ThisAspect.HowManyPagesLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Fit to how\nmany pages:')),
			ColLoc=0, ColSpan=1, RowSpan=2, NewRow=True, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.PagesAcrossLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Across')),
			ColLoc=1, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.PagesAcrossText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER), MinSizeY=25,
			Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnPagesAcrossTextCtrl,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, MinSizeX=100,
			ColLoc=2, ColSpan=1, DisplayMethod='StaticFromText')
		ThisAspect.ZoomLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Zoom (%)')),
			ColLoc=3, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.ZoomText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER), MinSizeY=25,
			Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnZoomTextCtrl,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, MinSizeX=50,
			ColLoc=4, ColSpan=1, DisplayMethod='StaticFromText')
		ThisAspect.PagesDownLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Down')), NewRow=True,
			ColLoc=1, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.PagesDownText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER), MinSizeY=25,
			Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnPagesDownTextCtrl,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, MinSizeX=100,
			ColLoc=2, ColSpan=1, DisplayMethod='StaticFromText')
		ThisAspect.NewPagePerRRCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('New page for each risk receptor')),
			Handler=ThisAspect.OnNewPagePerRRCheck, Events=[wx.EVT_CHECKBOX], ColLoc=3, ColSpan=3,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		# add widgets to PageLayoutBoxSubSizer
		ThisAspect.TextWidgets.extend(display_utilities.PopulateSizer(Sizer=PageLayoutBoxSubSizer, Widgets=[ThisAspect.PageSizeLabel,
			ThisAspect.PageSizeChoice, ThisAspect.PortraitRadio, ThisAspect.LandscapeRadio,
			ThisAspect.MarginLabel, ThisAspect.TopMarginLabel, ThisAspect.TopMarginText,
			ThisAspect.BottomMarginLabel, ThisAspect.BottomMarginText, ThisAspect.PageNumberingLabel,
				ThisAspect.PageNumberTopRadio, ThisAspect.PageNumberLeftRadio,
			ThisAspect.LeftMarginLabel, ThisAspect.LeftMarginText, ThisAspect.PageNumberBottomRadio,
				ThisAspect.PageNumberCentreRadio,
			ThisAspect.RightMarginLabel, ThisAspect.RightMarginText, ThisAspect.PageNumberNoneRadio,
				ThisAspect.PageNumberRightRadio,
			ThisAspect.HowManyPagesLabel, ThisAspect.PagesAcrossLabel, ThisAspect.PagesAcrossText,
				ThisAspect.ZoomLabel, ThisAspect.ZoomText,
			ThisAspect.PagesDownLabel, ThisAspect.PagesDownText, ThisAspect.NewPagePerRRCheck]))
		# make Style box and widgets
		ThisAspect.StyleBox = UIWidgetItem(StyleBoxSizer, HideMethod=lambda : StyleBoxSizer.ShowItems(False),
			ShowMethod=lambda : StyleBoxSizer.ShowItems(True), ColLoc=0, ColSpan=9, NewRow=True,
			SetFontMethod=lambda f: StyleBoxSizer.GetStaticBox().SetFont, Font=Fonts['SmallHeadingFont'])
#		ThisAspect.StyleLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Style')),
#			YGap=20, ColLoc=0, ColSpan=2, Font=Fonts['SmallHeadingFont'], NewRow=True)
		ThisAspect.FontLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Font:')),
			ColLoc=0, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.FontChoice = UIWidgetItem(wx.Choice(MyEditPanel, -1, size=(200, 25),
			choices=SystemFontNames),
			Handler=ThisAspect.OnFontChoice, Events=[wx.EVT_CHOICE], ColLoc=1, ColSpan=2)
		ThisAspect.ConnectorsAcrossPagesCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Add connectors across page breaks')),
			Handler=ThisAspect.OnConnectorsAcrossPagesCheck, Events=[wx.EVT_CHECKBOX], ColLoc=4, ColSpan=1, GapX=20)
		ThisAspect.DateLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1, _('Show date:')), NewRow=True,
			ColLoc=0, ColSpan=1, Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
		ThisAspect.DateChoice = UIWidgetItem(wx.Choice(MyEditPanel, -1, size=(100, 25),
			choices=[c.HumanName for c in DateChoices]),
			Handler=ThisAspect.OnDateChoice, Events=[wx.EVT_CHOICE], ColLoc=1, ColSpan=1)
		ThisAspect.CombineRRsCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Combine FTs for risk receptors where possible')),
			Handler=ThisAspect.OnCombineRRsCheck, Events=[wx.EVT_CHECKBOX], ColLoc=4, ColSpan=1)
		ThisAspect.CannotCalculateLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1,
			_('For values that cannot be calculated, show')), Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT,
			ColLoc=0, ColSpan=2, NewRow=True)
		ThisAspect.CannotCalculateText = UIWidgetItem(wx.TextCtrl(MyEditPanel, -1, style=wx.TE_PROCESS_ENTER), MinSizeY=25,
			Events=[wx.EVT_TEXT_ENTER], Handler=ThisAspect.OnCannotCalculateTextCtrl,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND, MinSizeX=100,
			ColLoc=2, ColSpan=1, DisplayMethod='StaticFromText')
		ThisAspect.ExpandGatesCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Expand logic gates')),
			Handler=ThisAspect.OnExpandGatesCheck, Events=[wx.EVT_CHECKBOX], ColLoc=4, ColSpan=1)
		ThisAspect.BlackWhiteCheck = UIWidgetItem(wx.CheckBox(MyEditPanel, -1, _('Monochrome')), NewRow=True,
			Handler=ThisAspect.OnBlackWhiteCheck, Events=[wx.EVT_CHECKBOX], ColLoc=4, ColSpan=1)
#		ThisAspect.DepictionLabel = UIWidgetItem(wx.StaticText(MyEditPanel, -1,
#			_('Fault tree depiction')),
#			YGap=20, ColLoc=0, ColSpan=2, Font=Fonts['SmallHeadingFont'], NewRow=True)
		ThisAspect.TextWidgets.extend(display_utilities.PopulateSizer(Sizer=StyleBoxSubSizer, Widgets=[
			ThisAspect.FontLabel, ThisAspect.FontChoice, ThisAspect.ConnectorsAcrossPagesCheck,
			ThisAspect.DateLabel, ThisAspect.DateChoice, ThisAspect.CombineRRsCheck,
			ThisAspect.CannotCalculateLabel, ThisAspect.CannotCalculateText,
			ThisAspect.ExpandGatesCheck, ThisAspect.BlackWhiteCheck]))
		# make Action box and widgets
		ThisAspect.ActionBox = UIWidgetItem(ActionBoxSizer, HideMethod=lambda : ActionBoxSizer.ShowItems(False),
			ShowMethod=lambda : ActionBoxSizer.ShowItems(True), ColLoc=9, ColSpan=1,
			SetFontMethod=lambda f: ActionBoxSizer.GetStaticBox().SetFont, Font=Fonts['SmallHeadingFont'])
		ThisAspect.CancelButton = UIWidgetItem(wx.Button(MyEditPanel, -1, _('Cancel')), GapX=42, NewRow=True,
			Handler=ThisAspect.OnCancelButton, Events=[wx.EVT_BUTTON], ColLoc=1, ColSpan=1, GapY=15,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND)
		ThisAspect.GoButton = UIWidgetItem(wx.Button(MyEditPanel, -1, _('Go')), NewRow=True,
			Handler=ThisAspect.OnGoButton, Events=[wx.EVT_BUTTON], ColLoc=1, ColSpan=1,
			Flags=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.EXPAND)
		display_utilities.PopulateSizer(Sizer=ActionBoxSubSizer, Widgets=[ThisAspect.CancelButton, ThisAspect.GoButton])

		# make list of widgets in this aspect
		ThisAspect.WidgetList = [ThisAspect.HeaderLabel,
			ThisAspect.FileBox,
			ThisAspect.PageLayoutBox,
#			ThisAspect.FilenameLabel, ThisAspect.FilenameText, ThisAspect.SelectButton, ThisAspect.FileTypeLabel,
#				ThisAspect.FileTypeChoice,
#			ThisAspect.OverwriteCheck,
#			ThisAspect.FilenameStatusMessage,
#			ThisAspect.ExportWhatLabel, ThisAspect.ShowHeaderCheck, ThisAspect.ShowFTCheck, ThisAspect.ShowOnlySelectedCheck,
			ThisAspect.ScopeBox,
#			ThisAspect.PageLayoutLabel,
#			ThisAspect.PageSizeLabel, ThisAspect.PageSizeChoice, ThisAspect.PortraitRadio, ThisAspect.LandscapeRadio,
#			ThisAspect.MarginLabel, ThisAspect.TopMarginLabel, ThisAspect.TopMarginText, ThisAspect.PageNumberingLabel,
#				ThisAspect.PageNumberTopRadio, ThisAspect.PageNumberLeftRadio,
#			ThisAspect.BottomMarginLabel, ThisAspect.BottomMarginText, ThisAspect.PageNumberBottomRadio,
#				ThisAspect.PageNumberCentreRadio,
#			ThisAspect.LeftMarginLabel, ThisAspect.LeftMarginText, ThisAspect.PageNumberNoneRadio,
#				ThisAspect.PageNumberRightRadio,
#			ThisAspect.RightMarginLabel, ThisAspect.RightMarginText,
#			ThisAspect.HowManyPagesLabel, ThisAspect.PagesAcrossLabel, ThisAspect.PagesAcrossText,
#				ThisAspect.PagesDownLabel, ThisAspect.PagesDownText, ThisAspect.NewPagePerRRCheck,
#			ThisAspect.ZoomLabel, ThisAspect.ZoomText,
			ThisAspect.StyleBox,
#			ThisAspect.StyleLabel,
#			ThisAspect.BlackWhiteCheck, ThisAspect.FontLabel, ThisAspect.FontChoice,
#			ThisAspect.DepictionLabel,
#			ThisAspect.ConnectorsAcrossPagesCheck, ThisAspect.CommentsCheck, ThisAspect.ActionsCheck, ThisAspect.ParkingCheck,
#			ThisAspect.CannotCalculateLabel, ThisAspect.CannotCalculateText, ThisAspect.CombineRRsCheck,
#			ThisAspect.ExpandGatesCheck, ThisAspect.DateLabel, ThisAspect.DateChoice,
			ThisAspect.ActionBox]
#			ThisAspect.CancelButton, ThisAspect.GoButton]
		# make list of widgets that need to be bound to their handlers in ActivateWidgetsInPanel()
		ThisAspect.WidgetsToActivate = [ThisAspect.FilenameLabel, ThisAspect.FilenameText, ThisAspect.SelectButton,
			ThisAspect.FileTypeLabel,
			ThisAspect.FileTypeChoice, ThisAspect.OverwriteCheck,
			ThisAspect.FilenameStatusMessage,
			ThisAspect.ExportWhatLabel, ThisAspect.ShowHeaderCheck, ThisAspect.ShowFTCheck, ThisAspect.ShowOnlySelectedCheck,
			ThisAspect.PageSizeLabel, ThisAspect.PageSizeChoice, ThisAspect.PortraitRadio, ThisAspect.LandscapeRadio,
			ThisAspect.MarginLabel, ThisAspect.TopMarginLabel, ThisAspect.TopMarginText, ThisAspect.PageNumberingLabel,
			ThisAspect.PageNumberTopRadio, ThisAspect.PageNumberLeftRadio,
			ThisAspect.BottomMarginLabel, ThisAspect.BottomMarginText, ThisAspect.PageNumberBottomRadio,
			ThisAspect.PageNumberCentreRadio,
			ThisAspect.LeftMarginLabel, ThisAspect.LeftMarginText, ThisAspect.PageNumberNoneRadio,
			ThisAspect.PageNumberRightRadio,
			ThisAspect.RightMarginLabel, ThisAspect.RightMarginText,
			ThisAspect.HowManyPagesLabel, ThisAspect.PagesAcrossLabel, ThisAspect.PagesAcrossText,
			ThisAspect.PagesDownLabel, ThisAspect.PagesDownText, ThisAspect.NewPagePerRRCheck,
			ThisAspect.ZoomLabel, ThisAspect.ZoomText,
			ThisAspect.BlackWhiteCheck, ThisAspect.FontLabel, ThisAspect.FontChoice,
			ThisAspect.ConnectorsAcrossPagesCheck, ThisAspect.CommentsCheck, ThisAspect.ActionsCheck, ThisAspect.ParkingCheck,
			ThisAspect.CannotCalculateLabel, ThisAspect.CannotCalculateText, ThisAspect.CombineRRsCheck,
			ThisAspect.ExpandGatesCheck, ThisAspect.DateLabel, ThisAspect.DateChoice,
			ThisAspect.CancelButton, ThisAspect.GoButton]
		return MyEditPanel.FTFullExportAspect

	def GetPageCountInfo(self, Zoom, ShowWhat, PageSizeLongAxis, PageSizeShortAxis, Orientation,
		TopMargin, BottomMargin, LeftMargin, RightMargin, PageNumberPos, NewPagePerRR, Font, ConnectorsAcrossPages,
		ShowComments, ShowActions, ShowParking, CannotCalculateText, CombineRRs, ExpandGates, DateKind, **Args):
		# calculate the number of pages required to export the FT
		# ShowWhat (str): what to include in the export. Contains some of 'Header', 'FT', 'OnlySelected'
#		# FT: a faulttree.FTForDisplay instance
		# return dict with args: PagesAcrossCount, PagesDownCount (2 x int)
#		assert type(FT).InternalName == 'FTTreeView' # confirming it's the correct class
		assert isinstance(Zoom, float)
		assert self.MinZoom <= Zoom <= self.MaxZoom
		assert isinstance(ShowWhat, str)
		assert isinstance(PageSizeLongAxis, (int, float))
		assert isinstance(PageSizeShortAxis, (int, float))
		assert Orientation in ['Portrait', 'Landscape']
		assert isinstance(TopMargin, (int, float))
		assert isinstance(BottomMargin, (int, float))
		assert isinstance(LeftMargin, (int, float))
		assert isinstance(RightMargin, (int, float))
		assert isinstance(PageNumberPos, str)
		assert isinstance(NewPagePerRR, bool)
		assert isinstance(Font, str)
		assert isinstance(ConnectorsAcrossPages, bool)
		assert isinstance(ShowComments, bool)
		assert isinstance(ShowActions, bool)
		assert isinstance(ShowParking, bool)
		assert isinstance(CannotCalculateText, str)
		assert isinstance(CombineRRs, bool)
		assert isinstance(ExpandGates, bool)
		assert DateKind in core_classes.DateChoices
		print('FR372 GetPageCountInfo: not implemented yet')
		return {'PagesAcrossCount': 2, 'PagesDownCount': 3}

	def DoExportFTToFile(self, FilePath, FileType,
		Zoom, ShowWhat, PageSizeLongAxis, PageSizeShortAxis,
		Orientation,
		TopMargin, BottomMargin, LeftMargin, RightMargin,
		PageNumberPos, FirstPageNumber, PageCountToShow, NewPagePerRR, Font,
		ConnectorsAcrossPages,
		ShowTexts, CannotCalculateText, CombineRRs, ExpandGates,
		DateKind, **Args):
		# Render the FT image in file(s)
		# return:
		# OK (bool) - whether export completed successfully without errors
		# Problem (str) - description of any problems encountered
		assert isinstance(FilePath, str)
		assert FileType in core_classes.ImageFileTypesSupported
		assert isinstance(Zoom, float)
		assert self.MinZoom <= Zoom <= self.MaxZoom
		assert isinstance(ShowWhat, str) # contains at least one of 'Header' and 'FT', plus optionally 'OnlySelected'
		assert isinstance(PageSizeLongAxis, (int, float))
		assert 0 < PageSizeLongAxis
		assert isinstance(PageSizeShortAxis, (int, float))
		assert 0 < PageSizeShortAxis
		assert Orientation in ['Portrait', 'Landscape']
		assert isinstance(TopMargin, (int, float))
		assert 0 <= TopMargin
		assert isinstance(BottomMargin, (int, float))
		assert 0 <= BottomMargin
		assert isinstance(LeftMargin, (int, float))
		assert 0 <= LeftMargin
		assert isinstance(RightMargin, (int, float))
		assert 0 <= RightMargin
		if Orientation == 'Portrait':
			assert PageSizeLongAxis > TopMargin + BottomMargin
			assert PageSizeShortAxis > LeftMargin + RightMargin
		else:
			assert PageSizeShortAxis > TopMargin + BottomMargin
			assert PageSizeLongAxis > LeftMargin + RightMargin
		assert isinstance(PageNumberPos, str)
		# confirm PageNumberPos contains exactly one of Top, Bottom, None; and exactly one of Left, Centre, Right
		assert int('Top' in PageNumberPos) + int('Bottom' in PageNumberPos) + int('None' in PageNumberPos) == 1
		assert int('Left' in PageNumberPos) + int('Centre' in PageNumberPos) + int('Right' in PageNumberPos) == 1
		assert isinstance(NewPagePerRR, bool)
		assert isinstance(Font, str)
		assert isinstance(ConnectorsAcrossPages, bool)
		assert isinstance(ShowTexts, str) # optionally contains 'Comments', 'ActionItems', 'ParkingLotItems'
		assert isinstance(CannotCalculateText, str)
		assert isinstance(CombineRRs, bool)
		assert isinstance(ExpandGates, bool)
		assert DateKind in core_classes.DateChoices
		print('FR575 DoExportFTToFile: not implemented yet')

	def __init__(self, Proj, PHAObj, DisplDevice, ParentWindow, Fonts, SystemFontNames, **Args):
		# __init__ for class FTFullExportViewport
		faulttree.FTForDisplay.__init__(self, Proj=Proj, PHAObj=PHAObj, DisplDevice=DisplDevice,
			ParentWindow=ParentWindow, **Args)
		self.SystemFontNames = SystemFontNames
		# make aspect object for dialogue
		self.DialogueAspect = self.MakeFTFullExportAspect(MyEditPanel=DisplDevice, Fonts=Fonts,
			SystemFontNames=SystemFontNames, DateChoices=Args['DateChoices'])

	def PrepareFullDisplay(self, XMLTree):
		# display dialogue in our display device to get export parameters from user
		print('FF434 starting PrepareFullDisplay')
		# first, unpack data into the FT
		super(type(self), self).PrepareFullDisplay(XMLTree)
#		self.UndoOnCancel = Args.get('UndoOnCancel', None)
		# build the dialogue: prefill widgets in new aspect and activate it
		self.DialogueAspect.Prefill(self.Proj, FT=self, SystemFontNames=self.SystemFontNames)
		self.DialogueAspect.SetWidgetVisibility()
#		self.DialogueAspect.Activate(WidgetsToActivate=self.DialogueAspect.WidgetsToActivate)
		self.DialogueAspect.Activate(WidgetsToActivate=self.DialogueAspect.WidgetsToActivate,
			TextWidgets=self.DialogueAspect.TextWidgets)
		# display aspect's sizer (containing all the visible widgets) in the edit panel
		self.DisplDevice.SetSizer(self.DialogueAspect.MySizer)

	def RenderInDC(self, TargetDC, FullRefresh=True, **Args): pass
		# nothing to do here - this Viewport doesn't draw in a DC - we need this stub to override the superclass's method

def GetFilenamesForMultipageExport(BasePath, FileType, PagesAcross, PagesDown):
	# return list of complete file paths (str) for a multipage export. See spec 392 for details
	# BasePath (str): full path of the filename without the sequential part
	# FileType (ImageFileType instance)
	# PagesAcross, PagesDown (2 x int): how many filenames required in X and Y directions; at least one must be >1
	assert isinstance(BasePath, str)
	assert isinstance(FileType, core_classes.ImageFileType)
	assert isinstance(PagesAcross, int)
	assert isinstance(PagesDown, int)
	assert PagesAcross > 0
	assert PagesDown > 0
	assert PagesAcross + PagesDown > 1
	RowsNumberingSystem = core_classes.UpperCaseLetterNumberSystem
	ColsNumberingSystem = core_classes.ArabicNumberSystem
	# First, find out where to insert the sequential part into BasePath
	# check if BasePath ends with its expected extension (e.g. jpg for a JPG file; case insensitive) preceded by
	# extension separator (usually '.')
	LenExtension = len(FileType.Extension)
	HasExpectedExtension = BasePath[-(LenExtension + 1):].upper() == os.extsep + FileType.Extension.upper()
	InsertIndex = len(BasePath) - len(FileType.Extension) - 1 if HasExpectedExtension else len(BasePath)
	AllFilePaths = [] # to contain all resulting file paths
	for ThisRow in range(PagesDown):
		SequentialPart = '-'
		# if multiple rows, add sequential letters (A, B, C... or AA, AB, AC...)
		if PagesDown > 1: SequentialPart += RowsNumberingSystem.HumanValue(TargetValue=ThisRow + 1,
			FieldWidth=RowsNumberingSystem.TargetFieldWidth(PagesDown))
		for ThisCol in range(PagesAcross):
			# if multiple columns, add sequential numbers (1, 2, 3... or 01, 02, 03...)
			if PagesAcross > 1: SequentialPartForCol = ColsNumberingSystem.HumanValue(TargetValue=ThisCol + 1,
				FieldWidth=ColsNumberingSystem.TargetFieldWidth(PagesAcross))
			else: SequentialPartForCol = ''
			# make filepath and append to list
			AllFilePaths.append(BasePath[:InsertIndex] + SequentialPart + SequentialPartForCol + BasePath[InsertIndex:])
	return AllFilePaths
