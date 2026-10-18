"""Plain-language interface texts (Spanish / English) and number formatting."""

LANGUAGES = {'es': 'Español', 'en': 'English'}

TEXT = {
    'es': {
        'app_tagline': 'El presupuesto municipal, explicado con claridad',
        'lang_label': 'Idioma',
        # Sidebar
        'no_dataset': 'No se encuentran los datos oficiales. Comprueba que la '
                      'carpeta data/conprel tiene sus archivos .csv.gz (en el '
                      'README se explica cómo prepararlos).',
        'sb_year': 'Año que quieres consultar',
        'sb_advanced': 'Opciones avanzadas',
        'sb_threshold': 'Avisar de cambios iguales o mayores que (%)',
        'sb_threshold_help': 'Las partidas que suban o bajen al menos este '
                             'porcentaje respecto al año anterior se marcan '
                             'para revisarlas con más detalle.',
        # Hero
        'council': 'el ayuntamiento',
        'council_of': 'el Ayuntamiento de {name}',
        'hero': 'En {year}, {who} prevé gastar {total}: {per_res} por cada '
                'habitante.',
        'hero_change_up': 'Es un {pct} más que en {prev}.',
        'hero_change_down': 'Es un {pct} menos que en {prev}.',
        'hero_change_same': 'La misma cantidad que en {prev}.',
        'hero_no_prev': 'No hay datos de {prev} para comparar.',
        'hero_balance_pos': 'Espera ingresar {bal} más de lo que gasta.',
        'hero_balance_neg': 'Espera gastar {bal} más de lo que ingresa.',
        'hero_balance_zero': 'Ingresos y gastos están equilibrados.',
        # KPI tiles
        'kpi_spend': 'Gasto total',
        'kpi_income': 'Ingresos totales',
        'kpi_per_res': 'Gasto por habitante',
        'kpi_balance': 'Ingresos menos gastos',
        'kpi_vs': 'respecto a {prev}',
        # Key points
        'kp_title': 'Lo más importante',
        'kp_largest': 'La partida más grande es {cat}: {share} de cada 100 € '
                      'que gasta el ayuntamiento ({per_res} por habitante).',
        'kp_rise': '{cat} es lo que más sube: {amount} más que en {prev} '
                   '({pct}).',
        'kp_fall': '{cat} es lo que más baja: {amount} menos que en {prev} '
                   '({pct}).',
        'kp_flagged_one': 'Una partida cambia un {thr} o más y conviene '
                          'revisarla: {cats}.',
        'kp_flagged_many': '{n} partidas cambian un {thr} o más y conviene '
                           'revisarlas: {cats}.',
        'kp_flagged_none': 'Ninguna partida cambia un {thr} o más respecto '
                           'a {prev}.',
        'kp_nominal': 'Las cifras están en euros de cada año, sin descontar '
                      'la inflación.',
        # Tabs
        'tab_spend': 'En qué se gasta',
        'tab_income': 'De dónde sale el dinero',
        'tab_change': 'Qué ha cambiado',
        'tab_data': 'Datos y descarga',
        'view_label': 'Ver como',
        'view_per_res': 'Por habitante',
        'view_total': 'Total',
        'view_share': 'De cada 100 €',
        'spend_intro': 'Cada barra es un área de gasto. Pasa el ratón por '
                       'encima para ver todas las cifras.',
        'income_intro': 'Cada barra es una fuente de ingresos del '
                        'ayuntamiento.',
        'no_rows': 'No hay datos de {kind} para {year}.',
        'kind_spend': 'gastos',
        'kind_income': 'ingresos',
        'change_intro': 'Cuánto sube o baja cada área de gasto respecto a '
                        '{prev}. Las barras con ⚑ superan el aviso del {thr}.',
        'change_none': 'No hay datos de {prev}, así que no se pueden calcular '
                       'los cambios. Elige otro año.',
        'trend_title': 'Evolución de cada área a lo largo de los años',
        'data_intro': 'Estos son los datos de {year} que usa la página. '
                      'Puedes descargarlos para reutilizarlos.',
        'download': 'Descargar datos de {year} (CSV)',
        # Table / chart labels
        'col_category': 'Área',
        'col_type': 'Tipo',
        'col_amount': 'Importe (€)',
        'col_year': 'Año',
        'col_prev': 'Año anterior (€)',
        'col_change': 'Cambio (%)',
        'col_flag': 'Revisar',
        'type_Expense': 'Gasto',
        'type_Income': 'Ingreso',
        'hover_total': 'Total',
        'hover_share': 'De cada 100 €',
        'hover_per_res': 'Por habitante',
        'axis_change': 'Cambio respecto a {prev} (%)',
        'axis_eur': 'Euros',
        # Glossary
        'a11y_title': 'Apariencia y accesibilidad',
        'a11y_theme': 'Modo de color',
        'a11y_theme_help': 'Automático sigue la configuración de tu '
                           'dispositivo. También puedes cambiarlo en el menú '
                           '⋮ de la esquina superior derecha.',
        'theme_auto': 'Automático',
        'theme_light': 'Claro',
        'theme_dark': 'Oscuro',
        'a11y_text': 'Tamaño del texto',
        'text_m': 'Normal',
        'text_l': 'Grande',
        'text_xl': 'Muy grande',
        'a11y_contrast': 'Alto contraste',
        'a11y_contrast_help': 'Texto más oscuro (o más claro en modo oscuro), '
                              'bordes gruesos y enlaces subrayados.',
        'a11y_spacing': 'Más espacio entre letras y líneas',
        'a11y_spacing_help': 'Puede facilitar la lectura, por ejemplo a '
                             'personas con dislexia.',
        'a11y_tables': 'Ver los datos de cada gráfico en una tabla',
        'a11y_tables_help': 'Útil si usas un lector de pantalla o prefieres '
                            'leer cifras a interpretar gráficos.',
        'a11y_saved': 'Tus opciones se guardan en la dirección de la página: '
                      'añádela a favoritos para conservarlas.',
        'chart_table': 'Datos del gráfico',
        'col_total': 'Total (€)',
        'col_share': 'De cada 100 €',
        'col_per_res': 'Por habitante (€)',
        'col_now': '{year} (€)',
        'glossary_title': 'Qué significan las palabras de esta página',
        'glossary': (
            '**Gasto por habitante:** el gasto dividido entre las personas '
            'empadronadas. Sirve para comparar municipios de distinto tamaño.\n\n'
            '**De cada 100 €:** qué parte del gasto total va a cada área. Si '
            'una partida tiene 25, uno de cada cuatro euros va a esa área.\n\n'
            '**Ingresos menos gastos:** si es positivo, el ayuntamiento prevé '
            'ingresar más de lo que gasta; si es negativo, gastar más de lo '
            'que ingresa.\n\n'
            '**Aviso de cambio:** marca las áreas que suben o bajan mucho de un '
            'año a otro. No significa que haya un error: es una invitación a '
            'mirar con más detalle.\n\n'
            '**Sin descontar la inflación:** las cifras no tienen en cuenta '
            'la subida de precios, así que parte de un aumento puede deberse '
            'a que todo cuesta más.'),
        'footer': 'OpenMunicipality es software libre con licencia MIT.',
    },
    'en': {
        'app_tagline': 'Your council budget, explained clearly',
        'lang_label': 'Language',
        'no_dataset': 'The official data could not be found. Check that the '
                      'data/conprel folder has its .csv.gz files (the README '
                      'explains how to build them).',
        'sb_year': 'Year you want to see',
        'sb_advanced': 'Advanced options',
        'sb_threshold': 'Flag changes of at least (%)',
        'sb_threshold_help': 'Budget lines that go up or down by at least '
                             'this percentage compared with the year before '
                             'are flagged for a closer look.',
        'council': 'the council',
        'council_of': '{name} council',
        'hero': 'In {year}, {who} plans to spend {total}: {per_res} for every '
                'resident.',
        'hero_change_up': "That's {pct} more than in {prev}.",
        'hero_change_down': "That's {pct} less than in {prev}.",
        'hero_change_same': "That's the same as in {prev}.",
        'hero_no_prev': 'There is no data for {prev} to compare with.',
        'hero_balance_pos': 'It expects to take in {bal} more than it spends.',
        'hero_balance_neg': 'It expects to spend {bal} more than it takes in.',
        'hero_balance_zero': 'Income and spending are balanced.',
        'kpi_spend': 'Total spending',
        'kpi_income': 'Total income',
        'kpi_per_res': 'Spending per resident',
        'kpi_balance': 'Income minus spending',
        'kpi_vs': 'since {prev}',
        'kp_title': 'Key points',
        'kp_largest': 'The biggest area is {cat}: {share} of every €100 the '
                      'council spends ({per_res} per resident).',
        'kp_rise': '{cat} goes up the most: {amount} more than in {prev} '
                   '({pct}).',
        'kp_fall': '{cat} goes down the most: {amount} less than in {prev} '
                   '({pct}).',
        'kp_flagged_one': 'One area changes by {thr} or more and is worth a '
                          'closer look: {cats}.',
        'kp_flagged_many': '{n} areas change by {thr} or more and are worth a '
                           'closer look: {cats}.',
        'kp_flagged_none': 'No area changes by {thr} or more compared with '
                           '{prev}.',
        'kp_nominal': "Amounts are in each year's euros and are not adjusted "
                      'for inflation.',
        'tab_spend': 'Where the money goes',
        'tab_income': 'Where the money comes from',
        'tab_change': 'What has changed',
        'tab_data': 'Data and download',
        'view_label': 'Show as',
        'view_per_res': 'Per resident',
        'view_total': 'Total',
        'view_share': 'Out of every €100',
        'spend_intro': 'Each bar is an area of spending. Hover over a bar to '
                       'see all the figures.',
        'income_intro': "Each bar is one of the council's sources of income.",
        'no_rows': 'There is no {kind} data for {year}.',
        'kind_spend': 'spending',
        'kind_income': 'income',
        'change_intro': 'How much each area of spending goes up or down '
                        'compared with {prev}. Bars marked ⚑ pass the {thr} '
                        'flag.',
        'change_none': "There is no data for {prev}, so changes can't be "
                       'worked out. Choose another year.',
        'trend_title': 'How each area has changed over the years',
        'data_intro': 'This is the {year} data the page uses. You can download '
                      'it to reuse it.',
        'download': 'Download {year} data (CSV)',
        'col_category': 'Area',
        'col_type': 'Type',
        'col_amount': 'Amount (€)',
        'col_year': 'Year',
        'col_prev': 'Previous year (€)',
        'col_change': 'Change (%)',
        'col_flag': 'Check',
        'type_Expense': 'Spending',
        'type_Income': 'Income',
        'hover_total': 'Total',
        'hover_share': 'Out of every €100',
        'hover_per_res': 'Per resident',
        'axis_change': 'Change compared with {prev} (%)',
        'axis_eur': 'Euros',
        'a11y_title': 'Appearance and accessibility',
        'a11y_theme': 'Colour mode',
        'a11y_theme_help': 'Automatic follows your device settings. You can '
                           'also change it from the ⋮ menu in the top right '
                           'corner.',
        'theme_auto': 'Automatic',
        'theme_light': 'Light',
        'theme_dark': 'Dark',
        'a11y_text': 'Text size',
        'text_m': 'Normal',
        'text_l': 'Large',
        'text_xl': 'Extra large',
        'a11y_contrast': 'High contrast',
        'a11y_contrast_help': 'Darker text (lighter in dark mode), thick '
                              'borders and underlined links.',
        'a11y_spacing': 'More space between letters and lines',
        'a11y_spacing_help': 'Can make reading easier, for example for '
                             'people with dyslexia.',
        'a11y_tables': 'Show the data behind each chart as a table',
        'a11y_tables_help': 'Useful with a screen reader, or if you prefer '
                            'reading figures to reading charts.',
        'a11y_saved': 'Your choices are saved in the page address: bookmark '
                      'it to keep them.',
        'chart_table': 'Chart data',
        'col_total': 'Total (€)',
        'col_share': 'Out of every €100',
        'col_per_res': 'Per resident (€)',
        'col_now': '{year} (€)',
        'glossary_title': 'What the words on this page mean',
        'glossary': (
            '**Spending per resident:** total spending divided by the number '
            'of registered residents. It lets you compare towns of different '
            'sizes.\n\n'
            '**Out of every €100:** the part of total spending that goes to '
            'each area. If an area has 25, one in every four euros goes '
            'there.\n\n'
            '**Income minus spending:** if it is positive, the council expects '
            'to take in more than it spends; if negative, to spend more than '
            'it takes in.\n\n'
            '**Change flag:** marks areas that go up or down a lot from one '
            "year to the next. It doesn't mean something is wrong: it's an "
            'invitation to look more closely.\n\n'
            '**Not adjusted for inflation:** the figures ignore price rises, '
            'so part of an increase may simply be because everything costs '
            'more.'),
        'footer': 'OpenMunicipality is free software under the MIT licence.',
    },
}

# Texts for the official-data (CONPREL) mode
TEXT['es'].update({
    'search_label': 'Municipio',
    'search_ph': 'Escribe el nombre de tu municipio',
    'search_none': 'No encontramos ningún municipio con ese nombre. Prueba '
                   'con una parte del nombre, por ejemplo «Rozas» o «Palma». '
                   'Si es tu municipio, puede que no haya enviado su '
                   'presupuesto al Ministerio de Hacienda.',
    'search_result': '{label}, {pop} habitantes',
    'and_more': ' y {n} más',
    'trend_note': 'Se muestran las seis áreas con más gasto en el último año; '
                  'el resto se suma en «Otras áreas».',
    'change_muni': 'Cambiar de municipio',
    'landing_title': '¿En qué gasta tu ayuntamiento?',
    'landing_sentence': 'OpenMunicipality explica en qué gasta su dinero '
                        'cada ayuntamiento de España.',
    'landing_text': 'Escribe el nombre de tu municipio y te explicamos su '
                    'presupuesto en lenguaje claro. Usamos los datos oficiales '
                    'que los ayuntamientos envían al Ministerio de Hacienda: '
                    '{n} municipios disponibles.',
    'stage_label': 'Qué quieres ver',
    'stage_budget': 'Lo previsto (presupuesto)',
    'stage_executed': 'Lo gastado (liquidación)',
    'sb_population_official': 'Habitantes según el padrón: {pop}',
    'hero_past': 'En {year}, {who} presupuestó gastar {total}: {per_res} por '
                 'cada habitante.',
    'hero_balance_pos_past': 'Previó ingresar {bal} más de lo que iba a '
                             'gastar.',
    'hero_balance_neg_past': 'Previó gastar {bal} más de lo que iba a '
                             'ingresar.',
    'hero_balance_zero_past': 'Ingresos y gastos estaban equilibrados.',
    'hero_balance_zero_exec': 'Ingresos y gastos quedaron equilibrados.',
    'hero_exec': 'En {year}, {who} gastó {total}: {per_res} por cada '
                 'habitante.',
    'hero_balance_pos_exec': 'Ingresó {bal} más de lo que gastó.',
    'hero_balance_neg_exec': 'Gastó {bal} más de lo que ingresó.',
    'kp_bench': 'En municipios de tamaño parecido ({band}) lo habitual es '
                'gastar {median} por habitante; {who_short} gasta {value}.',
    'who_short': 'este ayuntamiento',
    'bench_legend': 'Lo habitual en municipios de tamaño parecido',
    'this_council': 'Este ayuntamiento',
    'col_bench': 'Lo habitual en municipios parecidos (€/hab.)',
    'col_other': 'Municipio comparado (€/hab.)',
    'source_conprel': 'Fuente: Ministerio de Hacienda, CONPREL. {stage} {year}, '
                      'datos consolidados del ayuntamiento y sus organismos '
                      'autónomos. Población: padrón municipal.',
    'source_budget': 'Presupuestos',
    'source_executed': 'Liquidaciones',
    'band_0-1000': 'menos de 1.000 habitantes',
    'band_1000-5000': 'de 1.000 a 5.000 habitantes',
    'band_5000-20000': 'de 5.000 a 20.000 habitantes',
    'band_20000-50000': 'de 20.000 a 50.000 habitantes',
    'band_50000-100000': 'de 50.000 a 100.000 habitantes',
    'band_100000-500000': 'de 100.000 a 500.000 habitantes',
    'band_500000-inf': 'más de 500.000 habitantes',
    'glossary_extra': (
        '\n\n**Lo previsto y lo gastado:** el presupuesto es lo que el '
        'ayuntamiento planea gastar al empezar el año; la liquidación es lo que '
        'de verdad gastó al terminarlo (las obligaciones reconocidas). Durante '
        'el año el presupuesto se puede modificar, así que lo gastado puede '
        'quedar por encima o por debajo de lo previsto.\n\n'
        '**Lo habitual en municipios de tamaño parecido:** la cifra que está en '
        'el medio (la mediana). La mitad de los municipios de ese tamaño gasta '
        'más y la otra mitad, menos.'),
})
TEXT['en'].update({
    'search_label': 'Municipality',
    'search_ph': 'Type the name of your municipality',
    'search_none': "We couldn't find a municipality with that name. Try part "
                   'of the name, for example "Rozas" or "Palma". If it is '
                   'yours, it may not have sent its budget to the Ministry of '
                   'Finance.',
    'search_result': '{label}, {pop} residents',
    'and_more': ' and {n} more',
    'trend_note': 'Showing the six areas with the most spending in the latest '
                  'year; the rest are added up in "Other areas".',
    'change_muni': 'Change municipality',
    'landing_title': 'What does your council spend money on?',
    'landing_sentence': 'OpenMunicipality explains how every council in '
                        'Spain spends its money.',
    'landing_text': 'Type the name of your municipality and we will explain '
                    'its budget in plain language. We use the official data '
                    "that Spanish councils send to the Ministry of Finance: "
                    '{n} municipalities available.',
    'stage_label': 'What you want to see',
    'stage_budget': 'What was planned (budget)',
    'stage_executed': 'What was spent (outturn)',
    'sb_population_official': 'Registered residents: {pop}',
    'hero_past': 'In {year}, {who} planned to spend {total}: {per_res} for '
                 'every resident.',
    'hero_balance_pos_past': 'It expected to take in {bal} more than it '
                             'would spend.',
    'hero_balance_neg_past': 'It expected to spend {bal} more than it would '
                             'take in.',
    'hero_balance_zero_past': 'Income and spending were balanced.',
    'hero_balance_zero_exec': 'Income and spending were balanced.',
    'hero_exec': 'In {year}, {who} spent {total}: {per_res} for every '
                 'resident.',
    'hero_balance_pos_exec': 'It took in {bal} more than it spent.',
    'hero_balance_neg_exec': 'It spent {bal} more than it took in.',
    'kp_bench': 'In places of a similar size ({band}) the usual figure is '
                '{median} per resident; {who_short} spends {value}.',
    'who_short': 'this council',
    'bench_legend': 'Usual in municipalities of a similar size',
    'this_council': 'This council',
    'col_bench': 'Usual in similar municipalities (€/resident)',
    'col_other': 'Compared municipality (€/resident)',
    'source_conprel': 'Source: Spanish Ministry of Finance, CONPREL. {stage} '
                      '{year}, consolidated data for the council and its '
                      'agencies. Population: municipal register.',
    'source_budget': 'Budgets',
    'source_executed': 'Outturns',
    'band_0-1000': 'fewer than 1,000 residents',
    'band_1000-5000': '1,000 to 5,000 residents',
    'band_5000-20000': '5,000 to 20,000 residents',
    'band_20000-50000': '20,000 to 50,000 residents',
    'band_50000-100000': '50,000 to 100,000 residents',
    'band_100000-500000': '100,000 to 500,000 residents',
    'band_500000-inf': 'more than 500,000 residents',
    'glossary_extra': (
        '\n\n**Planned and spent:** the budget is what the council plans to '
        'spend at the start of the year; the outturn is what it actually spent '
        'by the end of it (recognised obligations). The budget can be changed '
        'during the year, so spending can end up above or below the plan.\n\n'
        '**Usual in municipalities of a similar size:** the figure in the '
        'middle (the median). Half of the municipalities of that size spend '
        'more and half spend less.'),
})


TEXT['es'].update({
    'view_by': 'Agrupar',
    'by_area': 'Por áreas',
    'by_kind': 'Por tipo de gasto',
    'kind_intro': 'Cada barra es un tipo de gasto: en qué se materializa el '
                  'dinero, sea cual sea el área.',
    'kp_invest': 'De cada 100 € de gasto, {share} se dedican a inversiones '
                 '(obras y equipamientos): {per_res} por habitante.',
    'kp_invest_bench': ' Lo habitual en municipios parecidos es {median}.',
    'kp_execution': 'En {year} presupuestó gastar {planned} y gastó {spent}: '
                    'el {rate} de lo previsto.',
    'nodata_title': 'No hay datos de {name} en la base del Ministerio de '
                    'Hacienda.',
    'nodata_text': 'Los ayuntamientos deben comunicar su presupuesto al '
                   'Ministerio de Hacienda, que publica los de quienes lo han '
                   'hecho. En esta aplicación no figura ningún presupuesto ni '
                   'liquidación de este ayuntamiento para {years}.',
    'nodata_foral': 'En Álava y Navarra, por su régimen foral, la mayoría de '
                    'ayuntamientos no aparecen en esta base de datos en los '
                    'últimos años.',
    'missing_years': 'Este ayuntamiento no figura en los datos de {years}.',
    'search_nodata': '{label}, sin datos',
    'sb_real': 'Descontar la inflación',
    'sb_real_help': 'Muestra los cambios después de restar la subida media de '
                    'los precios de cada año (IPC del INE).',
    'kp_real': 'Los cambios descuentan la inflación de {year}: {pi} de subida '
               'media de precios según el INE.',
    'real_unavailable': 'Todavía no hay dato de inflación media de {year}, así '
                        'que los cambios se muestran sin descontarla.',
    'hero_real': '(descontada la inflación)',
    'cmp_title': 'Comparar con otro municipio',
    'cmp_ph': 'Escribe el nombre del otro municipio',
    'press_enter': ' y pulsa Intro',
    'side_search': 'Buscar otro municipio',
    'side_search_ph': 'Escribe su nombre',
    'side_search_none': 'Ningún municipio con ese nombre.',
    'cmp_per_res_only': 'La comparación con {other} se ve en la vista '
                        '«{view}».',
    'cmp_clear': 'Quitar la comparación',
    'cmp_cancel': 'Cancelar',
    'cmp_active': ':material/compare_arrows: Comparando con **{other}**. Sus '
                  'cifras aparecen junto a las de este ayuntamiento en los '
                  'gráficos por habitante y en los puntos clave.',
    'cmp_no_year': '{other} no tiene datos de {year}.',
    'kp_compare': '{other} gasta {value} por habitante; este ayuntamiento, '
                  '{mine}.',
    'detail_label': 'Ver el detalle de un área',
    'detail_unavailable': 'El detalle por programas no está disponible: '
                          'faltan sus archivos (programs_*.csv.gz) en la '
                          'carpeta data/conprel.',
    'detail_ph': 'Elige un área',
    'detail_caption': 'Programas de gasto del área, con su nombre oficial.',
    'detail_missing': 'Este año el ayuntamiento no presentó el detalle por '
                      'programas. Hasta 2013, los municipios de menos de 5.000 '
                      'habitantes podían presentar el presupuesto solo por '
                      'áreas y políticas de gasto.',
    'share_title': 'Compartir',
    'share_image': 'Descargar imagen para redes sociales',
    'share_embed': 'Código para insertar este panel en una web',
    'share_embed_help': 'Copia este código en tu web o en tu artículo: '
                        'muestra este municipio sin los menús.',
    'card_title': 'Ayuntamiento de {name}, {stage} {year}',
    'card_stage_budget': 'presupuesto',
    'card_stage_executed': 'liquidación',
    'card_label': 'de gasto por habitante',
    'warn_title': 'Conviene comprobar estos datos',
    'warn_jump': 'El gasto total cambia un {pct} respecto al año anterior. '
                 'Puede ser real, pero también puede deberse a un presupuesto '
                 'prorrogado o a un error al enviar los datos.',
    'warn_unusual': 'El gasto por habitante es muy distinto del habitual en '
                    'municipios de tamaño parecido. En municipios muy pequeños '
                    'o con mucha población de temporada puede ser normal.',
    'warn_deficit': 'Los datos muestran más gasto previsto que ingresos '
                    'previstos. Conviene comprobarlo en la fuente.',
    'warn_population': 'La población cambia más de un 20 % entre un año y '
                       'otro, lo que altera las cifras por habitante.',
    'warn_rollover': 'Todas las partidas son idénticas a las del año '
                     'anterior. Lo más probable es que sea un presupuesto '
                     'prorrogado: el ayuntamiento no aprobó uno nuevo y siguió '
                     'con el del año anterior.',
    'warn_source': 'Las cifras son las que el ayuntamiento comunicó al '
                   'Ministerio de Hacienda.',
    'warn_jump_executed': 'El gasto total cambia un {pct} respecto al año '
                          'anterior. Puede ser real, por ejemplo por una obra '
                          'grande, pero también puede deberse a un error al '
                          'enviar los datos.',
    'missing_years_executed': 'No hay liquidación de este ayuntamiento para '
                              '{years}.',
    'coverage_executed': 'Lo gastado está disponible para {years}.',
    'warn_execution': 'Lo gastado es el {pct} de lo previsto, muy lejos de lo '
                      'habitual. Puede deberse a cambios grandes en el '
                      'presupuesto durante el año o a un error al enviar los '
                      'datos.',
    'plan_title': '¿Se gastó lo previsto?',
    'plan_intro': 'Lo que el ayuntamiento presupuestó para {year} al empezar el '
                  'año y lo que de verdad gastó, por habitante.',
    'plan_planned': 'Previsto (presupuesto)',
    'plan_spent': 'Gastado (liquidación)',
    'plan_gap': 'La mayor diferencia está en «{area}»: se previeron {planned} y '
                'se gastaron {spent}.',
    'col_planned': 'Previsto (€/hab.)',
    'col_spent': 'Gastado (€/hab.)',
    'col_rate': 'Gastado de lo previsto (%)',
    'glossary_kinds': (
        '\n\n**Tipo de gasto:** el mismo dinero visto según en qué se '
        'materializa: sueldos del personal, compras y servicios contratados, '
        'subvenciones, inversiones (obras y equipamientos) o pago de la '
        'deuda.\n\n'
        '**Descontar la inflación:** restar la subida media de precios del '
        'año para ver si de verdad se gasta más o solo cuesta más lo mismo.'),
})
TEXT['en'].update({
    'view_by': 'Group',
    'by_area': 'By area',
    'by_kind': 'By type of spending',
    'kind_intro': 'Each bar is a type of spending: what the money pays for, '
                  'whatever the area.',
    'kp_invest': 'Out of every €100 spent, {share} goes to investment (works '
                 'and equipment): {per_res} per resident.',
    'kp_invest_bench': ' The usual figure in places of a similar size is '
                       '{median}.',
    'kp_execution': 'In {year} it planned to spend {planned} and spent '
                    '{spent}: {rate} of what was planned.',
    'nodata_title': 'There is no data for {name} in the Ministry of Finance '
                    'database.',
    'nodata_text': 'Councils must send their budget to the Ministry of '
                   'Finance, which publishes those that have done so. This '
                   'app has no budget or outturn from this council for '
                   '{years}.',
    'nodata_foral': 'In Álava and Navarre, which have their own (foral) '
                    'financial regime, most councils have not been in this '
                    'database in recent years.',
    'missing_years': 'This council is not in the data for {years}.',
    'search_nodata': '{label}, no data',
    'sb_real': 'Adjust for inflation',
    'sb_real_help': "Shows changes after taking away each year's average "
                    'price rise (INE consumer price index).',
    'kp_real': 'Changes are adjusted for {year} inflation: an average price '
               'rise of {pi} according to the INE.',
    'real_unavailable': 'There is no average inflation figure for {year} yet, '
                        'so changes are shown without adjusting for it.',
    'hero_real': '(adjusted for inflation)',
    'cmp_title': 'Compare with another municipality',
    'cmp_ph': 'Type the name of the other municipality',
    'press_enter': ' and press Enter',
    'side_search': 'Find another municipality',
    'side_search_ph': 'Type its name',
    'side_search_none': 'No municipality with that name.',
    'cmp_per_res_only': 'The comparison with {other} is shown in the '
                        '"{view}" view.',
    'cmp_clear': 'Remove comparison',
    'cmp_cancel': 'Cancel',
    'cmp_active': ':material/compare_arrows: Comparing with **{other}**. Its '
                  'figures appear next to this council\'s in the per-resident '
                  'charts and in the key points.',
    'cmp_no_year': '{other} has no data for {year}.',
    'kp_compare': '{other} spends {value} per resident; this council, '
                  '{mine}.',
    'detail_label': 'See the detail of an area',
    'detail_unavailable': 'Programme detail is not available: its files '
                          '(programs_*.csv.gz) are missing from the '
                          'data/conprel folder.',
    'detail_ph': 'Choose an area',
    'detail_caption': "The area's spending programmes, with their official "
                      '(Spanish) names.',
    'detail_missing': 'This year the council did not report programme detail. '
                      'Until 2013, municipalities with fewer than 5,000 '
                      'residents could report spending only by area and '
                      'policy.',
    'share_title': 'Share',
    'share_image': 'Download image for social media',
    'share_embed': 'Code to embed this view in a website',
    'share_embed_help': 'Paste this code into your website or article: it '
                        'shows this municipality without the menus.',
    'card_title': '{name} council, {stage} {year}',
    'card_stage_budget': 'budget',
    'card_stage_executed': 'outturn',
    'card_label': 'spending per resident',
    'warn_title': 'These figures are worth checking',
    'warn_jump': 'Total spending changes by {pct} compared with the previous '
                 'year. It may be real, but it can also come from a budget '
                 'rolled over from the year before or an error when the data '
                 'was sent.',
    'warn_unusual': 'Spending per resident is very different from the usual '
                    'figure in municipalities of a similar size. In very small '
                    'or seasonal-tourism municipalities this can be normal.',
    'warn_deficit': 'The data shows more planned spending than planned '
                    'income. It is worth checking the source.',
    'warn_population': 'Population changes by more than 20% from one year to '
                       'the next, which affects the per-resident figures.',
    'warn_rollover': 'Every budget line is identical to the year before. Most '
                     'likely the budget was rolled over: the council did not '
                     'approve a new one and kept the previous year\'s.',
    'warn_source': 'The figures are those the council sent to the Ministry of '
                   'Finance.',
    'warn_jump_executed': 'Total spending changes by {pct} compared with the '
                          'previous year. It may be real, for example because '
                          'of a large building project, but it can also come '
                          'from an error when the data was sent.',
    'missing_years_executed': 'There is no outturn from this council for '
                              '{years}.',
    'coverage_executed': 'What was spent is available for {years}.',
    'warn_execution': 'Spending was {pct} of what was planned, far from the '
                      'usual. It may come from large changes to the budget '
                      'during the year or from an error when the data was '
                      'sent.',
    'plan_title': 'Was the money spent as planned?',
    'plan_intro': 'What the council budgeted for {year} at the start of the '
                  'year and what it actually spent, per resident.',
    'plan_planned': 'Planned (budget)',
    'plan_spent': 'Spent (outturn)',
    'plan_gap': 'The biggest difference is in "{area}": {planned} was planned '
                'and {spent} was spent.',
    'col_planned': 'Planned (€/resident)',
    'col_spent': 'Spent (€/resident)',
    'col_rate': 'Spent out of planned (%)',
    'glossary_kinds': (
        '\n\n**Type of spending:** the same money seen by what it pays for: '
        'staff salaries, purchases and contracted services, grants, '
        'investment (works and equipment) or debt payments.\n\n'
        '**Adjust for inflation:** take away the year\'s average price rise '
        'to see whether more is really being spent or the same things simply '
        'cost more.'),
})

# Plain-language names for the official spending policies (grouped) and
# income chapters produced by scripts/build_conprel.py
OFFICIAL_CATEGORIES = {
    'S_DEBT': ('Pago de la deuda', 'Debt repayments'),
    'S_SAFETY': ('Policía, tráfico y protección civil',
                 'Police, traffic and civil protection'),
    'S_HOUSING': ('Vivienda y urbanismo', 'Housing and urban planning'),
    'S_COMMUNITY': ('Agua, basuras, limpieza y alumbrado',
                    'Water, waste, street cleaning and lighting'),
    'S_ENVIRONMENT': ('Parques y medio ambiente', 'Parks and environment'),
    'S_PENSIONS': ('Pensiones y ayudas al personal',
                   'Pensions and staff benefits'),
    'S_SOCIAL': ('Servicios sociales', 'Social services'),
    'S_EMPLOYMENT': ('Fomento del empleo', 'Employment support'),
    'S_HEALTH': ('Salud', 'Health'),
    'S_EDUCATION': ('Educación', 'Education'),
    'S_CULTURE': ('Cultura y fiestas', 'Culture and festivities'),
    'S_SPORT': ('Deporte', 'Sport'),
    'S_TRANSPORT': ('Transporte público', 'Public transport'),
    'S_INFRA': ('Calles, carreteras e infraestructuras',
                'Roads, streets and infrastructure'),
    'S_ECONOMY': ('Comercio, turismo, agricultura e innovación',
                  'Trade, tourism, farming and innovation'),
    'S_GOV': ('Gobierno y administración del ayuntamiento',
              'Council government and administration'),
    'S_TRANSFERS': ('Aportaciones a otras administraciones',
                    'Payments to other public bodies'),
    'OTHER': ('Otras áreas', 'Other areas'),
    'K_STAFF': ('Personal (sueldos y cotizaciones)',
                'Staff (salaries and contributions)'),
    'K_PURCHASES': ('Compras y servicios contratados',
                    'Purchases and contracted services'),
    'K_GRANTS': ('Subvenciones y ayudas', 'Grants and subsidies'),
    'K_INVEST': ('Inversiones (obras y equipamientos)',
                 'Investment (works and equipment)'),
    'K_DEBT': ('Deuda (intereses y devoluciones)',
               'Debt (interest and repayments)'),
    'K_OTHER': ('Otros (fondo para imprevistos y préstamos concedidos)',
                'Other (contingency fund and loans granted)'),
    'I1': ('Impuestos directos (IBI, vehículos, actividades económicas)',
           'Direct taxes (property, vehicles, business activity)'),
    'I2': ('Impuestos indirectos (obras y otros)',
           'Indirect taxes (building works and others)'),
    'I3': ('Tasas y precios públicos', 'Fees and charges'),
    'I4': ('Dinero de otras administraciones (Estado, comunidad…)',
           'Money from other governments (State, region…)'),
    'I5': ('Rentas del patrimonio municipal', 'Income from council property'),
    'I6': ('Venta de terrenos y otros bienes', 'Sale of land and other assets'),
    'I7': ('Ayudas de otras administraciones para inversiones',
           'Grants from other governments for investment'),
    'I8': ('Devolución de préstamos y depósitos',
           'Loans and deposits repaid to the council'),
    'I9': ('Préstamos que pide el ayuntamiento', 'New borrowing'),
}

# Display names for the categories of the bundled sample dataset.
CATEGORY_NAMES = {
    'es': {
        'Social Services': 'Servicios sociales',
        'Education & Culture': 'Educación y cultura',
        'Environment & Parks': 'Medio ambiente y parques',
        'Urban Infrastructure': 'Infraestructura urbana',
        'Public Safety': 'Seguridad ciudadana',
        'Local Taxes': 'Impuestos municipales',
        'State Transfers': 'Transferencias del Estado',
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    text = TEXT.get(lang, TEXT['en']).get(key) or TEXT['en'][key]
    return text.format(**kwargs) if kwargs else text


DATASET_CATEGORIES: dict[str, tuple[str, str]] = {}


def register_categories(table) -> None:
    """Names for the codes of a plugged-in dataset (columns code, name_es,
    name_en); they take precedence over the built-in ones."""
    DATASET_CATEGORIES.update({
        row.code: (row.name_es, row.name_en if isinstance(row.name_en, str)
                   else row.name_es) for row in table.itertuples()})


def category_name(lang: str, name: str) -> str:
    if name in DATASET_CATEGORIES:
        return DATASET_CATEGORIES[name][0 if lang == 'es' else 1]
    if name in OFFICIAL_CATEGORIES:
        return OFFICIAL_CATEGORIES[name][0 if lang == 'es' else 1]
    return CATEGORY_NAMES.get(lang, {}).get(name, name)


def integer(value: float, lang: str) -> str:
    return _group(value, 0, lang)


def _group(value: float, decimals: int, lang: str) -> str:
    text = f'{value:,.{decimals}f}'
    if lang == 'es':  # 1,234.5 -> 1.234,5
        text = text.replace(',', '\x00').replace('.', ',').replace('\x00', '.')
    return text


def money(value: float, lang: str, decimals: int = 2) -> str:
    """€537.74 (en) / 537,74 € (es)."""
    sign = '−' if value < 0 else ''
    body = _group(abs(value), decimals, lang)
    return f'{sign}{body} €' if lang == 'es' else f'{sign}€{body}'


def money_compact(value: float, lang: str) -> str:
    """€114.0M (en) / 114,0 M€ (es)."""
    sign = '−' if value < 0 else ''
    v = abs(value)
    for size, en_s, es_s in ((1e9, 'bn', ' mil M€'), (1e6, 'M', ' M€'),
                             (1e3, 'k', ' mil €')):
        if v >= size:
            body = _group(v / size, 1, lang)
            return (f'{sign}{body}{es_s}' if lang == 'es'
                    else f'{sign}€{body}{en_s}')
    return money(value, lang, 0)


def money_words(value: float, lang: str) -> str:
    """'114 millones de euros' / '€114 million' for plain-language sentences."""
    v = abs(value)
    if v >= 1e9 and lang != 'es':  # Spanish usage keeps "6.557 millones"
        return f'€{_group(v / 1e9, 1, lang)} billion'
    if v >= 1e6:
        n = v / 1e6
        body = _group(n, 0 if n >= 100 or n == int(n) else 1, lang)
        return (f'{body} millones de euros' if lang == 'es'
                else f'€{body} million')
    return money(v, lang, 0)


def pct(value: float, lang: str, decimals: int = 1, signed: bool = False) -> str:
    sign = ('+' if value > 0 else '−' if value < 0 else '') if signed else (
        '−' if value < 0 else '')
    body = _group(abs(value), decimals, lang)
    return f'{sign}{body} %' if lang == 'es' else f'{sign}{body}%'


MONTHS = {
    'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
           'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July',
           'August', 'September', 'October', 'November', 'December'],
}


def long_date(day, lang: str) -> str:
    """'13 de junio de 2015' / '13 June 2015'."""
    month = MONTHS.get(lang, MONTHS['en'])[day.month - 1]
    return (f'{day.day} de {month} de {day.year}' if lang == 'es'
            else f'{day.day} {month} {day.year}')


def short_date(day, lang: str) -> str:
    """'13/06/2015' / '13 Jun 2015'."""
    if lang == 'es':
        return f'{day.day:02d}/{day.month:02d}/{day.year}'
    return f'{day.day} {MONTHS["en"][day.month - 1][:3]} {day.year}'


# Mayors (Ministry of Territorial Policy) lined up with the budgets
TEXT['es'].update({
    'tab_mayors': 'Quién gobernaba',
    'mayor_side_title': 'Alcaldía en {year}',
    'mayor_side_row': '{who}: {start} – {end}',
    'mayor_side_open': '{who}: desde el {start}',
    'mayor_side_none': 'No hay datos de alcaldía para {year}. El registro '
                       'disponible va del {first} al {last}.',
    'kp_mayor_budget': 'El 1 de enero de {year} ocupaba la alcaldía {who}, '
                       'en el cargo desde el {since}.',
    'kp_mayor_budget_earlier': 'El 1 de enero de {year} ocupaba la alcaldía '
                               '{who}, en el cargo al menos desde el {since}.',
    'kp_mayor_first': ' Era el primer presupuesto de su alcaldía.',
    'kp_mayor_during': ' Durante el año la alcaldía pasó a {who}.',
    'then': ' y después a ',
    'on_day': ' el {day}',
    'from_day': ' desde el {day}',
    'kp_mayor_exec': 'Durante la mayor parte de {year} ocupó la alcaldía '
                     '{who}.',
    'kp_mayor_split': 'En {year} la alcaldía cambió de manos, sin que nadie la ocupara más de medio año: {who}.',
    'change_mayor': 'Entre {prev} y {year} cambió la alcaldía: de {before} a '
                    '{after}. Los cambios de esta página no se deben '
                    'necesariamente a ese relevo.',
    'mayors_intro': 'Gasto por habitante de cada año sobre quién ocupaba la '
                    'alcaldía. Cada franja es una alcaldía.',
    'mayors_rules': 'Cómo se asigna cada año: el presupuesto, a quien ocupaba '
                    'la alcaldía el 1 de enero (normalmente quien lo '
                    'preparó); lo gastado, a quien la ocupó más de medio año. '
                    'Las listas aparecen como las registra el Ministerio de '
                    'Política Territorial: «C. ELECTORAL» es una coalición '
                    'electoral y «OTROS», agrupaciones locales o partidos '
                    'pequeños. Que el gasto suba o baje con una alcaldía no '
                    'demuestra que se deba a ella: también influyen la '
                    'economía, las normas estatales y las decisiones del '
                    'pleno. Del mandato 2023–2027 solo se conoce la '
                    'alcaldía actual.',
    'mayors_none': 'No hay datos de alcaldía para este municipio.',
    'mayors_gap': 'Sin datos de alcaldía antes del {first} ni después del '
                  '{last}.',
    'mayors_now': 'Con {who}, el gasto presupuestado por habitante pasó de '
                  '{first} en {y0} a {last} en {y1} ({change}).',
    'mayors_now_real': ' Descontada la inflación: {change}.',
    'mayors_now_one': 'Con {who} hay un solo presupuesto en los datos ({y0}): '
                      '{first} por habitante.',
    'mayors_table': 'Balance por alcaldía',
    'mayors_table_intro': 'Solo cuentan los años con datos. «Prorrogados» son '
                          'los presupuestos que repiten el del año anterior '
                          'área por área porque no se aprobó uno nuevo.',
    'mayors_open_end': '\\* Fin de los datos disponibles: pudo seguir en el '
                       'cargo después.',
    'legend_budget': 'Previsto (presupuesto)',
    'legend_spent': 'Gastado (liquidación)',
    'axis_per_res': '€ por habitante',
    'election': 'Elecciones {year}',
    'hover_mayor': 'Alcaldía',
    'col_mayor': 'Alcaldía',
    'col_lists': 'Lista',
    'col_from': 'Desde',
    'col_to': 'Hasta',
    'col_budgets': 'Presupuestos',
    'col_first': 'Primer presup. (€/hab.)',
    'col_last': 'Último presup. (€/hab.)',
    'col_change_term': 'Cambio (%)',
    'col_change_term_real': 'Cambio sin inflación (%)',
    'col_invest': 'Inversión media (€/hab.)',
    'col_rolled': 'Prorrogados',
    'col_spent_pct': 'Gastado de lo previsto (mediana, %)',
    'download_mayors': 'Descargar la lista de alcaldías (CSV)',
    'source_mayors': 'Alcaldías: Ministerio de Política Territorial, '
                     'relación de alcaldes por mandato (2007–2023, desde '
                     '2010) y alcaldía vigente del mandato 2023–2027.',
    'at_least': '{day} o antes',
    'mayor_side_gap': 'Sin datos de alcaldía del {start} al {end}.',
    'mayor_current_only': 'Del mandato 2023–2027 el Ministerio solo publica '
                          'quién ocupa hoy la alcaldía, no quién la ocupó '
                          'antes.',
    'glossary_mayors': (
        '\n\n**Alcaldía y listas:** quién ocupaba la alcaldía y con qué lista '
        'se registró. «C. ELECTORAL» es una coalición electoral; «OTROS», '
        'agrupaciones de electores o partidos pequeños; «IND», '
        'independiente; «N.ADS.», no adscrito (dejó su grupo); «C. GEST.», '
        'comisión gestora (gobierno provisional sin alcaldía electa).'),
})
TEXT['en'].update({
    'tab_mayors': 'Who was in office',
    'mayor_side_title': 'Mayor in {year}',
    'mayor_side_row': '{who}: {start} – {end}',
    'mayor_side_open': '{who}: since {start}',
    'mayor_side_none': 'There is no mayor data for {year}. The register '
                       'available runs from {first} to {last}.',
    'kp_mayor_budget': 'On 1 January {year} the mayor was {who}, in office '
                       'since {since}.',
    'kp_mayor_budget_earlier': 'On 1 January {year} the mayor was {who}, in '
                               'office since at least {since}.',
    'kp_mayor_first': ' It was the first budget of that mayoralty.',
    'kp_mayor_during': ' During the year the mayoralty passed to {who}.',
    'then': ' and then to ',
    'on_day': ' on {day}',
    'from_day': ' from {day}',
    'kp_mayor_exec': 'For most of {year} the mayor was {who}.',
    'kp_mayor_split': 'In {year} the mayoralty changed hands and nobody held it for more than half the year: {who}.',
    'change_mayor': 'Between {prev} and {year} the mayor changed: from '
                    '{before} to {after}. The changes on this page are not '
                    'necessarily due to that.',
    'mayors_intro': 'Spending per resident each year against who was mayor. '
                    'Each band is one mayoralty.',
    'mayors_rules': 'How each year is assigned: the budget, to whoever was '
                    'mayor on 1 January (usually who prepared it); what was '
                    'spent, to whoever was mayor for more than half the year. '
                    'Lists appear as the Ministry of Territorial Policy '
                    'registers them: "C. ELECTORAL" is an electoral coalition '
                    'and "OTROS" local groups or small parties. Spending going '
                    'up or down under a mayor does not prove the mayor caused '
                    'it: the economy, national rules and council decisions '
                    'also play a part. For the 2023–2027 term only the '
                    'current mayor is known.',
    'mayors_none': 'There is no mayor data for this council.',
    'mayors_gap': 'No mayor data before {first} or after {last}.',
    'mayors_now': 'Under {who}, planned spending per resident went from '
                  '{first} in {y0} to {last} in {y1} ({change}).',
    'mayors_now_real': ' After inflation: {change}.',
    'mayors_now_one': 'Under {who} there is one budget in the data ({y0}): '
                      '{first} per resident.',
    'mayors_table': 'Record of each mayoralty',
    'mayors_table_intro': 'Only years with data count. "Rolled over" are '
                          'budgets that repeat the previous year area by area '
                          'because no new one was approved.',
    'mayors_open_end': '\\* End of the data available: may have stayed in '
                       'office afterwards.',
    'legend_budget': 'Planned (budget)',
    'legend_spent': 'Spent (outturn)',
    'axis_per_res': '€ per resident',
    'election': '{year} election',
    'hover_mayor': 'Mayor',
    'col_mayor': 'Mayor',
    'col_lists': 'List',
    'col_from': 'From',
    'col_to': 'To',
    'col_budgets': 'Budgets',
    'col_first': 'First budget (€/res.)',
    'col_last': 'Last budget (€/res.)',
    'col_change_term': 'Change (%)',
    'col_change_term_real': 'Change after inflation (%)',
    'col_invest': 'Average investment (€/res.)',
    'col_rolled': 'Rolled over',
    'col_spent_pct': 'Spent out of planned (median, %)',
    'download_mayors': 'Download the list of mayors (CSV)',
    'source_mayors': 'Mayors: Spanish Ministry of Territorial Policy, list of '
                     'mayors per term (2007–2023, from 2010) and current '
                     'mayors of the 2023–2027 term.',
    'at_least': '{day} or earlier',
    'mayor_side_gap': 'No mayor data from {start} to {end}.',
    'mayor_current_only': 'For the 2023–2027 term the Ministry only '
                          'publishes who is mayor today, not who was before.',
    'glossary_mayors': (
        '\n\n**Mayor and list:** who was mayor and the list they were '
        'registered under. "C. ELECTORAL" is an electoral coalition; '
        '"OTROS", groups of voters or small parties; "IND", independent; '
        '"N.ADS.", non-attached (left their group); "C. GEST.", management '
        'committee (a caretaker government without an elected mayor).'),
})

TEXT['es']['executed_missing'] = (
    'Falta el archivo de lo gastado (data/conprel/lines_executed.csv.gz), '
    'por eso no se puede elegir entre lo previsto y lo gastado. Está en el '
    'archivo OpenMunicipality_v1.0.0_parte2_gastado.zip.')
TEXT['en']['executed_missing'] = (
    'The outturn file (data/conprel/lines_executed.csv.gz) is missing, so '
    'planned and spent cannot be shown side by side. It is in '
    'OpenMunicipality_v1.0.0_parte2_gastado.zip.')
