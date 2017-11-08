from edc_navbar import NavbarItem, site_navbars, Navbar

specimens = Navbar(name='specimens')

specimens.append_item(
    NavbarItem(name='requisition',
               title='Requisitions',
               label='requisition',
               url_name=f'edc_lab_dashboard:requisition_listboard_url'))

specimens.append_item(
    NavbarItem(name='receive',
               title='Receive',
               label='receive',
               url_name=f'edc_lab_dashboard:receive_listboard_url'))

specimens.append_item(
    NavbarItem(name='process',
               title='Process',
               label='process',
               url_name=f'edc_lab_dashboard:process_listboard_url'))

specimens.append_item(
    NavbarItem(name='pack',
               title='Pack',
               label='pack',
               url_name=f'edc_lab_dashboard:pack_listboard_url'))

specimens.append_item(
    NavbarItem(name='manifest',
               title='Manifest',
               label='manifest',
               url_name=f'edc_lab_dashboard:manifest_listboard_url'))

specimens.append_item(
    NavbarItem(name='aliquot',
               title='Aliquot',
               label='aliquot',
               url_name=f'edc_lab_dashboard:aliquot_listboard_url'))

specimens.append_item(
    NavbarItem(name='result',
               title='Result',
               label='result',
               url_name=f'edc_lab_dashboard:result_listboard_url'))

specimens.append_item(
    NavbarItem(name='specimens',
               label='specimens',
               fa_icon='fa-flask',
               url_name=f'edc_lab_dashboard:home_url'))

site_navbars.register(specimens)
