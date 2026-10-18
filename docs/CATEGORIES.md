# From official spending policies to plain-language areas

The 24 spending policies of the Spanish local budget structure (Orden
EHA/3565/2008, "política de gasto") are grouped into 17 areas named in
everyday words. The grouping is `POLICY_GROUPS` in
`scripts/build_conprel.py`; the names shown in the app are in
`modules/i18n.py`. Both can be changed and the dataset rebuilt.

| Area code | Name in the app (es) | Name in the app (en) | Official policies |
|---|---|---|---|
| `S_DEBT` | Pago de la deuda | Debt repayments | 01 Deuda pública |
| `S_SAFETY` | Policía, tráfico y protección civil | Police, traffic and civil protection | 13 Seguridad y movilidad ciudadana |
| `S_HOUSING` | Vivienda y urbanismo | Housing and urban planning | 15 Vivienda y urbanismo |
| `S_COMMUNITY` | Agua, basuras, limpieza y alumbrado | Water, waste, street cleaning and lighting | 16 Bienestar comunitario |
| `S_ENVIRONMENT` | Parques y medio ambiente | Parks and environment | 17 Medio ambiente |
| `S_PENSIONS` | Pensiones y ayudas al personal | Pensions and staff benefits | 21 Pensiones; 22 Otras prestaciones económicas a favor de empleados |
| `S_SOCIAL` | Servicios sociales | Social services | 23 Servicios sociales y promoción social |
| `S_EMPLOYMENT` | Fomento del empleo | Employment support | 24 Fomento del empleo |
| `S_HEALTH` | Salud | Health | 31 Sanidad |
| `S_EDUCATION` | Educación | Education | 32 Educación |
| `S_CULTURE` | Cultura y fiestas | Culture and festivities | 33 Cultura |
| `S_SPORT` | Deporte | Sport | 34 Deporte |
| `S_ECONOMY` | Comercio, turismo, agricultura e innovación | Trade, tourism, farming and innovation | 41 Agricultura, ganadería y pesca; 42 Industria y energía; 43 Comercio, turismo y pequeñas y medianas empresas; 46 Investigación, desarrollo e innovación; 49 Otras actuaciones de carácter económico |
| `S_TRANSPORT` | Transporte público | Public transport | 44 Transporte público |
| `S_INFRA` | Calles, carreteras e infraestructuras | Roads, streets and infrastructure | 45 Infraestructuras |
| `S_GOV` | Gobierno y administración del ayuntamiento | Council government and administration | 91 Órganos de gobierno; 92 Servicios de carácter general; 93 Administración financiera y tributaria |
| `S_TRANSFERS` | Aportaciones a otras administraciones | Payments to other public bodies | 94 Transferencias a otras Administraciones Públicas |

Income is shown by the nine economic chapters (`I1`–`I9`). Spending by type
groups the economic chapters: staff (chapter 1), purchases and services (2),
current grants (4), investment (6, real investment, and 7, capital
transfers), debt (3, interest, and 9, repayments) and other (5, contingency
fund, and 8, financial assets). See `KINDS` in `modules/conprel.py`.
