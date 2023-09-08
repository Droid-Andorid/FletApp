import asyncio
import flet as ft
import database
# import asyncio
import botcontrol
from time import sleep


APP_VERSION = 0.0_1
__version__ = "0.0.1"

class Navigation(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.rail = ft.NavigationRail(label_type=ft.NavigationRailLabelType.ALL,
                                      min_width=100, min_extended_width=100, leading=ft.Text("Main menu"), trailing=ft.Text(f"Version program {__version__}", expand=True),
                                      group_alignment=-0.9,
                                      extended=False,
                                      destinations=[
                                          ft.NavigationRailDestination(icon=ft.icons.WEBHOOK,
                                                                       selected_icon=ft.icons.WEBHOOK_ROUNDED, label="Webhook"),
                                          ft.NavigationRailDestination(icon=ft.icons.ANDROID,
                                                                       selected_icon=ft.icons.ANDROID_ROUNDED, label="Bot",
                                                                       label_content=ft.Text("Bot control")),
                                          ft.NavigationRailDestination(icon=ft.icons.SETTINGS,
                                                                       selected_icon=ft.icons.SETTINGS_ROUNDED,
                                                                       label="Settings"),
                                          ft.NavigationRailDestination(icon=ft.icons.EXIT_TO_APP, label="Exit",
                                                                       selected_icon=ft.icons.EXIT_TO_APP_ROUNDED, padding=ft.padding.only(top=100))
                                          ], on_change=self.check_nav)

        self.webhook_view = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                      alignment=ft.MainAxisAlignment.CENTER)

        self.bot_view = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                  alignment=ft.MainAxisAlignment.CENTER)

        self.settings_view = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                       alignment=ft.MainAxisAlignment.CENTER)

        self.webhook_view.visible = False
        self.settings_view.visible = False
        self.bot_view.visible = False

        self.main_screen = ft.Row([self.rail, ft.VerticalDivider(width=1), self.view_column(ft.MainAxisAlignment.CENTER)])

        self.dlg = ft.AlertDialog(modal=True, title=ft.Text("Exit"), content=ft.Text("You sure?"),
                                  actions=[ft.TextButton("Yes", on_click=self.destroy),
                                           ft.TextButton("No", on_click=self.close_dlg)])

    def build(self):
        return self.main_screen

    def view_column(self, align: ft.MainAxisAlignment):
        self.webhook_view.alignment = align

        self.bot_view.alignment = align

        self.settings_view.alignment = align
        return ft.Row([self.webhook_view, self.bot_view, self.settings_view], alignment=align)


    def check_nav(self, e):
        select = self.rail.selected_index
        if select == 0:
            if len(self.webhook_view.controls) < 1:
                self.webhook_view.controls.append(Webhook(self.webhook_view))
            self.webhook_view.visible = True
            self.settings_view.visible = False
            self.bot_view.visible = False
            self.update()
        elif select == 1:
            if len(self.bot_view.controls) < 1:
                self.bot_view.controls.append(BotControlPage())
            self.bot_view.alignment = ft.MainAxisAlignment.CENTER
            self.webhook_view.visible = False
            self.settings_view.visible = False
            self.bot_view.visible = True
            self.update()
        elif select == 2:
            if len(self.settings_view.controls) < 1:
                self.settings_view.controls.append(SettingsPage())
            self.settings_view.alignment = ft.MainAxisAlignment.CENTER
            self.webhook_view.visible = False
            self.settings_view.visible = True
            self.bot_view.visible = False
            self.update()
        elif select == 3:
            self.page.dialog = self.dlg
            self.dlg.open = True
            self.rail.selected_index = None
            self.rail.update()
            self.page.update()

    def destroy(self, e):
        self.page.window_destroy()

    def close_dlg(self, e):
        self.dlg.open = False
        self.page.update()


class Webhook(ft.UserControl):
    def __init__(self, screen_view):
        super().__init__(screen_view)
        self.select = ft.Tabs(selected_index=0, on_change=self.tabs_change,
                              tabs=[ft.Tab(text="Embed"), ft.Tab(text="Non-embed")])

        self.screen = screen_view

        self.url = ft.TextField(label="URL webhook", prefix_icon="webhook", width=800, password=True, on_change=self.url_change)
        self.btn_save = ft.IconButton(icon=ft.icons.SAVE_AS, selected_icon=ft.icons.SAVE, bgcolor=ft.colors.ON_SECONDARY, on_click=self.save_url, tooltip="Save url")
        self.btn_select = ft.IconButton(icon=ft.icons.SELECT_ALL, selected_icon=ft.icons.SELECT_ALL_ROUNDED, on_click=self.select_dlg, tooltip="Select save url")
        self.url_text = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
        self.url_create = False

        self.dlg_s = ft.AlertDialog(modal=False, title=ft.Text("Information"), content=ft.Text("Successful"))
        self.dlg_e = ft.AlertDialog(modal=True, title=ft.Text("Error"), content=ft.Text("Unsuccessful!, Unknown error"),
                                    actions=[ft.TextButton(text="Close", on_click=self.close_dlg_e)])
        self.dlg_ve = ft.AlertDialog(modal=True, title=ft.Text("Error"), content=ft.Text("Wrong enter value"),
                                     actions=[ft.TextButton(text="Close", on_click=self.close_dlg_ve)])

        self.dlg_url_e = ft.AlertDialog(modal=False, title=ft.Text("Error"), content=ft.Text("Enter your url webhook"))

        self.field_name = ft.Ref[ft.TextField]()

        self.dlg_save = ft.AlertDialog(modal=True, title=ft.Text("Save url webhook"),
                                       content=ft.Text("Enter name for save"),
                                       actions=[ft.TextField(hint_text="Name", ref=self.field_name, on_change=self.save_name_change),
                                                ft.TextButton("Cancel", on_click=self.close_dlg_save), ft.FilledButton("Save", on_click=self.save)])
        self.name = ""

        self.drop_save_url = ft.Dropdown(label="Please select save url", suffix_icon=ft.icons.SAVE,
                                         options=[opt for opt in database.get_dropdown_webhook()])

        self.dlg_select = ft.AlertDialog(modal=True, title=ft.Text("Select url"), content=self.drop_save_url,
                                         actions=[ft.Row([ft.TextButton("Cancel", on_click=self.close_dlg_select), ft.FilledButton("Select", on_click=self.select_url)])
                                                  ])

        self.emb = ft.Container(content=EmbPage(self.url, self.dlg_s, self.dlg_ve, self.dlg_e),
                                padding=ft.padding.all(0), alignment=ft.alignment.top_center)
        self.non_emb = ft.Container(content=NonEmbPage(self.url, self.url_text, self.dlg_s, self.dlg_ve),
                                    padding=ft.padding.all(0), alignment=ft.alignment.top_center)

    def build(self):
        return self.select

    def save_url(self, e):
        if not self.url.value.startswith("https://discord.com/api/webhooks/"):
            self.page.dialog = self.dlg_url_e
            self.dlg_url_e.open = True
            self.page.update()
        else:
            self.page.dialog = self.dlg_save
            self.dlg_save.open = True
            self.page.update()

    def tabs_change(self, e):
        select: str = self.select.tabs[self.select.selected_index].text
        if not self.url_create:
            self.create_main()
            self.screen.update()

        if select == "Embed":
            self.non_emb.visible = False
            self.emb.visible = True
            self.screen.update()
        elif select == "Non-embed":
            self.url.on_submit = self
            self.emb.visible = False
            self.non_emb.visible = True
            self.screen.update()

    def url_change(self, e):
        if not self.url.value.startswith("https://discord.com/api/webhooks/"):
            self.url.error_text = "Enter URL webhook"
            self.url_text.update()
        else:
            self.url.error_text = ""
            self.url_text.update()

    def save_name_change(self, e):
        if self.field_name.current.value == "":
            self.field_name.current.error_text = "Enter name"
            self.field_name.current.update()
        else:
            self.field_name.current.error_text = ""
            self.field_name.current.update()

    def save(self, e):
        try:
            database.save_hook_url(self.field_name.current.value, self.url.value)
            self.create = False
            self.dlg_save.open = False
            if not self.create:
                self.create = True
                self.url_text.controls.append(ft.Text("Successful saved", color="green"))
                self.page.update()
                self.url_text.update()
                sleep(10)
                self.create = False
                self.url_text.controls.pop(-1)
                self.url_text.update()
        except Exception as e:
            self.page.dialog = self.dlg_e
            self.dlg_e.open = True
            self.page.update()
            print(e)

    def select_dlg(self, e):
        self.page.dialog = self.dlg_select
        self.dlg_select.open = True
        self.page.update()
        self.check_new_save()

    def select_url(self, e):
        print(self.drop_save_url.value)
        save_name = database.get_save_url(self.drop_save_url.value)
        self.url.value = save_name
        self.url_text.update()

    def check_new_save(self):
        try:
            if self.name != database.get_last_name():
                self.name = database.get_last_name()
                print(database.get_last_name())
                self.drop_save_url.options.append(ft.dropdown.Option(f"{database.get_last_name()}"))
                self.drop_save_url.update()
        except Exception as e:
            print(e)

    def create_main(self):
        self.url_text.controls.append(self.url)
        self.url_text.controls.append(self.btn_save)
        self.url_text.controls.append(self.btn_select)
        self.screen.controls.append(self.url_text)
        self.screen.controls.append(self.emb)
        self.screen.controls.append(self.non_emb)
        self.emb.visible = False
        self.non_emb.visible = False
        self.url_create = True

    def close_dlg_e(self, e):
        self.dlg_e.open = False
        self.page.update()

    def close_dlg_ve(self, e):
        self.dlg_ve.open = False
        self.page.update()

    def close_dlg_save(self, e):
        self.dlg_save.open = False
        self.page.update()

    def close_dlg_select(self, e):
        self.dlg_select.open = False
        self.page.update()


class NonEmbPage(ft.UserControl):
    def __init__(self, url_field, url_control, dlg, dlg_ve):
        super().__init__(url_field, url_control, dlg, dlg_ve)
        self.url = url_field
        self.url_text = url_control
        self.text = ft.TextField(label="Enter your text", width=500, multiline=True, max_lines=1000)
        self.btn_send_non = ft.FilledTonalButton(text="Send", icon="send", on_click=self.non_embed_message)
        self.non_emb = ft.Row(alignment=ft.MainAxisAlignment.CENTER)

        self.dlg = dlg
        self.dlg_ve = dlg_ve

    def build(self):
        # self.url_text.controls.append(self.url)
        self.non_emb.controls.append(self.text)
        self.non_emb.controls.append(self.btn_send_non)

        return self.non_emb

    def non_embed_message(self, e):
        import snakehook
        try:
            if self.url.value.startswith("https://discord.com/api/webhooks/"):
                snakehook.start_non_embed(text=self.text.value, url=self.url.value)
                self.page.dialog = self.dlg
                self.dlg.open = True
                self.page.update()
            else:
                raise ValueError
        except ValueError:
            self.page.dialog = self.dlg_ve
            self.dlg_ve.open = True
            self.page.update()


class EmbPage(ft.UserControl):
    def __init__(self, url_field, dlg, dlg_ve, dlg_e):
        super().__init__(url_field, dlg, dlg_ve, dlg_e)
        self.amount = 0
        self.url = url_field
        self.emb_title = ft.TextField(label="Title embed", hint_text="Обов'язково вести")
        self.emb_desc = ft.TextField(label="Description embed", hint_text="Обов'язково вести")
        self.color = ft.Dropdown(width=200, label="Select your color", prefix_icon=ft.icons.COLOR_LENS, value="Default",
                                 options=[ft.dropdown.Option("Default"),
                                          ft.dropdown.Option("Blue"),
                                          ft.dropdown.Option("Blurple"),
                                          ft.dropdown.Option("Dark_blue"),
                                          ft.dropdown.Option("Green"),
                                          ft.dropdown.Option("Brand_green"),
                                          ft.dropdown.Option("Dark_green")])
        self.colour = ft.Dropdown(width=200, label="Select your colour", prefix_icon=ft.icons.COLOR_LENS,
                                  value="Default",
                                  options=[ft.dropdown.Option("Default"),
                                           ft.dropdown.Option("Blue"),
                                           ft.dropdown.Option("Blurple"),
                                           ft.dropdown.Option("Dark_blue"),
                                           ft.dropdown.Option("Green"),
                                           ft.dropdown.Option("Brand_green"),
                                           ft.dropdown.Option("Dark_green")])
        self.btn_send_emb = ft.FilledTonalButton(text="Send", icon="send", on_click=self.emb_message)
        self.fld_btn = ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_fld)
        self.emb = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
        self.emb_add = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
        self.fld = ft.Column()

        self.dlg = dlg
        self.dlg_ve = dlg_ve
        self.dlg_e = dlg_e

    def build(self):
        if len(self.emb.controls) <= 1:
            self.emb.controls.append(self.emb_title)
            self.emb.controls.append(self.emb_desc)
            self.emb.controls.append(self.fld_btn)
            self.emb.controls.append(self.btn_send_emb)
            self.fld_btn.disabled = True

            self.emb_add.controls.append(self.color)
            self.emb_add.controls.append(self.colour)

            return ft.Column([self.emb, self.emb_add])

    def emb_message(self, e):
        import snakehook
        try:
            if self.url.value.startswith("https://discord.com/api/webhooks/"):
                if not self.emb_title.value == "" and not self.emb_desc == "":
                    snakehook.start_embed(self.url.value, self.emb_title.value, self.emb_desc.value,
                                          self.colour.value, self.color, self.amount, self.items)
                    self.page.dialog = self.dlg
                    self.dlg.open = True
                    self.page.update()
                else:
                    raise ValueError
            else:
                raise ValueError
        except ValueError:
            self.page.dialog = self.dlg_ve
            self.dlg_ve.open = True
            self.page.update()
        except AttributeError:
            snakehook.start_embed(self.url.value, self.emb_title.value, self.emb_desc.value,
                                  self.colour.value, self.color.value)
            self.page.dialog = self.dlg
            self.dlg.open = True
            self.page.update()
        # except:
        #     self.page.dialog = self.dlg_e
        #     self.dlg_e.open = True
        #     self.page.update()

    async def add_fld(self, e):
        self.amount += 1

        self.field_title = ft.TextField(label=f"Title field {self.amount}", width=600)
        self.field_desc = ft.TextField(label=f"Description field {self.amount}", width=600)

        self.fld.controls.append(self.field_title)
        self.fld.controls.append(self.field_desc)
        self.fld.controls.append(self.btn_send_emb)

        self.items = []

        def colum(align: ft.MainAxisAlignment):
            self.fld.alignment = align
            return self.fld

        try:
            self.emb.controls.remove(self.btn_send_emb)
        except ValueError:
            self.fld.controls.remove(self.btn_send_emb)

        self.page.add(ft.Row([colum(ft.MainAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER))
        self.page.update()

        while len(self.field_title.value) <= 1:
            sleep(20)
        while len(self.field_desc.value) <= 1:
            sleep(20)
        else:
            self.items.append(self.field_title.value)
            self.items.append(self.field_desc.value)
            print(self.items)


class BotControlPage(ft.UserControl):
    def __init__(self):
        super().__init__()

        self.token = ft.TextField(label="Token bot", suffix_icon=ft.icons.TOKEN, password=True, width=620)
        self.btn_save = ft.IconButton(icon=ft.icons.SAVE_AS, selected_icon=ft.icons.SAVE, bgcolor=ft.colors.ON_SECONDARY, on_click=self.open_dlg_save)
        self.btn_select = ft.IconButton(icon=ft.icons.SELECT_ALL_SHARP, selected_icon=ft.icons.SELECT_ALL, on_click=self.open_dlg_select)
        self.up_area = ft.Row([self.token, self.btn_save, self.btn_select])
        self.pb = ft.ProgressBar(width=200, color=ft.colors.LIGHT_BLUE)
        self.progress_area = ft.Column([ft.Text("Checking"), self.pb])
        self.progress_area.visible = False
        self.btn_test = ft.FilledButton("Test connections", icon=ft.icons.CHECK, disabled=False, on_click=self.check_bot)

        self.btn_start = ft.FilledButton("Start bot", icon=ft.icons.PLAY_ARROW, disabled=True)
        self.btn_start_settings = ft.FilledTonalButton("Setings start", icon=ft.icons.SETTINGS_ACCESSIBILITY)
        self.btn_reload = ft.FilledButton("Reload bot", icon=ft.icons.RESTART_ALT, disabled=True)
        self.btn_stop = ft.FilledButton("Shutdown bot", icon="stop", disabled=True)

        self.field_name = ft.Ref[ft.TextField]()

        self.dlg_save = ft.AlertDialog(modal=True, title=ft.Text("Save api key bot"), content=ft.TextField(label="Enter name save", ref=self.field_name),
                                       actions=[ft.Row([ft.TextButton("Cancel", on_click=self.close_dlg_save), ft.FilledTonalButton("Save", on_click=self.save_api)])])

        self.dropdown_save_api = ft.Dropdown(label="Please select save url", suffix_icon=ft.icons.SAVE,
                                         options=[opt for opt in database.get_dropdown_api()])

        self.dlg_select = ft.AlertDialog(modal=True, title=ft.Text("Select url"), content=self.dropdown_save_api,
                                         actions=[ft.Row([ft.TextButton("Cancel", on_click=self.close_dlg_select),
                                                          ft.FilledButton("Select", on_click=self.select_api)])
                                                  ])
        self.main_screen = ft.Column([self.up_area, self.progress_area, self.btn_test, ft.Row([self.btn_start, self.btn_start_settings]), self.btn_reload, self.btn_stop],
                                     horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.alignment.center)
        self.name = ""

        self.git_url = ft.TextField(label="Git url")
        # self.direct = ft.FilePicker()
        self.direct_git = ft.TextField(label="Direction")
        self.btn_clone = ft.FilledButton("Git clone")
        self.start_settings_view = ft.Column([self.git_url, self.direct_git, self.btn_clone])

    def build(self):
        return self.main_screen

    def check_bot(self, e):
        self.progress_area.visible = True
        self.progress_area.update()
        botcontrol.startup_test(self.token.value)
        self.progress_area.visible = False
        self.up_area.controls.append(ft.Text("Bot working", color="green"))
        self.up_area.update()
        self.progress_area.update()
        self.btn_start.disabled = False
        self.btn_stop.disabled = False
        self.update()
        sleep(10)
        self.up_area.controls.pop()
        self.up_area.update()

    def open_dlg_save(self, e):
        if len(self.token.value) >= 70:
            self.page.dialog = self.dlg_save
            self.dlg_save.open = True
            self.page.update()

    def close_dlg_save(self, e):
        self.dlg_save.open = False
        self.page.update()

    def open_dlg_select(self, e):
        self.page.dialog = self.dlg_select
        self.dlg_select.open = True
        self.page.update()
        self.check_new_save()

    def save_api(self, e):
        if len(self.field_name.current.value) >= 1:
            database.save_bot_api(self.field_name.current.value, self.token.value)
            self.dlg_save.open = False
            self.up_area.controls.append(ft.Text("Success", color="green"))
            self.up_area.update()
            self.page.update()
            sleep(10)
            self.up_area.controls.pop(-1)
            self.up_area.update()

    def select_api(self, e):
        print(self.dropdown_save_api.value)
        save_name = database.get_save_api(self.dropdown_save_api.value)
        self.token.value = save_name
        self.token.update()
        self.dlg_select.open = False
        self.page.update()

    def check_new_save(self):
        try:
            if self.name != database.get_last_save_api_name():
                self.name = database.get_last_save_api_name()
                print(database.get_last_save_api_name())
                self.dropdown_save_api.options.append(ft.dropdown.Option(f"{database.get_last_save_api_name()}"))
                self.dropdown_save_api.update()
        except Exception as e:
            print(e)

    def close_dlg_select(self, e):
        self.dlg_select.open = False
        self.page.update()

    # def start_settings(self, e):


    # Створити функцію для скачування репозиторія
    # Створити функцію для вибирання файлу
    # Створити функцію для запуску бота


class SettingsPage(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.debugs = ft.Switch(label="DEBUG", on_change=self.debug_check)
        self.soundpad = ft.Switch(label="Soundpad mode", disabled=True)
        self.btn_theme = ft.Switch(label="Dark mode", on_change=self.change_theme, value=True, tooltip="Turn on Dark mode")
        self.check_upd_btn = ft.ElevatedButton(text="check updates", icon=ft.icons.CHECK, disabled=True)

    def build(self):
        return ft.Row([self.debugs, self.soundpad, self.btn_theme, ft.Column([self.check_upd_btn])])

    def debug_check(self, e):
        if self.debugs.value is True:
            import logging

            self.logger = logging.getLogger("flet_core")
            self.logger.disabled = False
            handler = logging.FileHandler(filename="App.log", encoding="utf-8", mode="w")
            handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(handler)
        else:
            self.logger.disabled = True

    def change_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.page.update()
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.page.update()


def main(page: ft.Page):
    page.title = "Control bot(pre-alpha)"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_min_height = 500
    page.window_min_width = 1000
    page.window_center()

    page.on_connect = database.initialize_db()

    start_screen = Navigation()
    start_screen.expand = True
    page.controls.append(start_screen)
    page.update()


if __name__ == '__main__':
    ft.app(target=main)
