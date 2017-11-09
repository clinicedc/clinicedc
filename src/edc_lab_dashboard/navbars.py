from edc_navbar import NavbarItem, site_navbars, Navbar

specimens = Navbar(name='specimens')

specimens.append_item(
    NavbarItem(name='requisition',
               label='Requisition',
               url_name=f'edc_lab_dashboard:requisition_listboard_url'))

specimens.append_item(
    NavbarItem(name='receive',
               label='Receive',
               url_name=f'edc_lab_dashboard:receive_listboard_url'))

specimens.append_item(
    NavbarItem(name='process',
               label='Process',
               url_name=f'edc_lab_dashboard:process_listboard_url'))

specimens.append_item(
    NavbarItem(name='pack',
               label='Pack',
               url_name=f'edc_lab_dashboard:pack_listboard_url'))

specimens.append_item(
    NavbarItem(name='manifest',
               label='Manifest',
               url_name=f'edc_lab_dashboard:manifest_listboard_url'))

specimens.append_item(
    NavbarItem(name='aliquot',
               label='Aliquot',
               url_name=f'edc_lab_dashboard:aliquot_listboard_url'))

specimens.append_item(
    NavbarItem(name='result',
               label='Result',
               url_name=f'edc_lab_dashboard:result_listboard_url'))

specimens.append_item(
    NavbarItem(name='specimens',
               title='specimens',
               fa_icon='fa-flask',
               url_name=f'edc_lab_dashboard:home_url'))

site_navbars.register(specimens)
