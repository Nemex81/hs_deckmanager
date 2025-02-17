import wx
import wx.ribbon

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        # Creazione del pannello principale
        panel = wx.Panel(self)

        # Creazione della barra multifunzione (ribbon bar)
        ribbon_bar = wx.ribbon.RibbonBar(panel, wx.ID_ANY)

        # Creazione di un pannello nella barra multifunzione
        home_panel = wx.ribbon.RibbonPage(ribbon_bar, wx.ID_ANY, "Home")

        # Creazione di una categoria nella barra multifunzione
        tools_panel = wx.ribbon.RibbonPanel(home_panel, wx.ID_ANY, "Tools")
        tools_toolbar = wx.ribbon.RibbonButtonBar(tools_panel, wx.ID_ANY)

        # Aggiunta di un pulsante alla barra degli strumenti
        tools_toolbar.AddButton(wx.ID_ANY, "New", wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_OTHER, wx.Size(32, 32)))
        tools_toolbar.AddButton(wx.ID_ANY, "Open", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, wx.Size(32, 32)))
        tools_toolbar.AddButton(wx.ID_ANY, "Save", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_OTHER, wx.Size(32, 32)))

        # Impostazione della barra multifunzione
        ribbon_bar.Realize()

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(ribbon_bar, 0, wx.EXPAND)
        panel.SetSizer(sizer)

        # Impostazione delle dimensioni della finestra
        self.SetSize((800, 600))
        self.SetTitle("wx.Ribbon Example")
        self.Centre()
        # sposta il focus sul primo pulsante disponibile


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        frame.Show(True)
        return True

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()