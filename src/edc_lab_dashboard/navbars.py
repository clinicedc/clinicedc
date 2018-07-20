from edc_navbar import NavbarItem, site_navbars, Navbar

from .dashboard_urls import dashboard_urls

specimens = Navbar(name='specimens')

specimens.append_item(
    NavbarItem(name='requisition',
               label='Requisition',
               url_name=dashboard_urls.get('requisition_listboard_url')))

specimens.append_item(
    NavbarItem(name='receive',
               label='Receive',
               url_name=dashboard_urls.get('receive_listboard_url')))

specimens.append_item(
    NavbarItem(name='process',
               label='Process',
               url_name=dashboard_urls.get('process_listboard_url')))

specimens.append_item(
    NavbarItem(name='pack',
               label='Pack',
               url_name=dashboard_urls.get('pack_listboard_url')))

specimens.append_item(
    NavbarItem(name='manifest',
               label='Manifest',
               url_name=dashboard_urls.get('manifest_listboard_url')))

specimens.append_item(
    NavbarItem(name='aliquot',
               label='Aliquot',
               url_name=dashboard_urls.get('aliquot_listboard_url')))

specimens.append_item(
    NavbarItem(name='result',
               label='Result',
               url_name=dashboard_urls.get('result_listboard_url')))

specimens.append_item(
    NavbarItem(name='specimens',
               title='specimens',
               fa_icon='fas fa-flask',
               url_name='#',
               active=True))

site_navbars.register(specimens)
