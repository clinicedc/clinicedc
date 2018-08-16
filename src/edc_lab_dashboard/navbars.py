from edc_navbar import NavbarItem, site_navbars, Navbar

from .dashboard_urls import dashboard_urls

specimens = Navbar(name='specimens')

specimens.append_item(
    NavbarItem(name='requisition',
               label='Requisition',
               permission_codename='nav_lab_requisition',
               url_name=dashboard_urls.get('requisition_listboard_url')))

specimens.append_item(
    NavbarItem(name='receive',
               label='Receive',
               permission_codename='nav_lab_receive',
               url_name=dashboard_urls.get('receive_listboard_url')))

specimens.append_item(
    NavbarItem(name='process',
               label='Process',
               permission_codename='nav_lab_process',
               url_name=dashboard_urls.get('process_listboard_url')))

specimens.append_item(
    NavbarItem(name='pack',
               label='Pack',
               permission_codename='nav_lab_pack',
               url_name=dashboard_urls.get('pack_listboard_url')))

specimens.append_item(
    NavbarItem(name='manifest',
               label='Manifest',
               permission_codename='nav_lab_manifest',
               url_name=dashboard_urls.get('manifest_listboard_url')))

specimens.append_item(
    NavbarItem(name='aliquot',
               label='Aliquot',
               permission_codename='nav_lab_aliquot',
               url_name=dashboard_urls.get('aliquot_listboard_url')))

specimens.append_item(
    NavbarItem(name='result',
               label='Result',
               permission_codename='nav_lab_result',
               url_name=dashboard_urls.get('result_listboard_url')))

specimens.append_item(
    NavbarItem(name='specimens',
               title='specimens',
               fa_icon='fas fa-flask',
               url_name='#',
               permission_codename='nav_lab_section',
               active=True))

site_navbars.register(specimens)
