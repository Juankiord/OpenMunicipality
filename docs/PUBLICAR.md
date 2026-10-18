# Cómo publicar OpenMunicipality (paso a paso)

Todo lo necesario ya está en esta carpeta: código, datos, tests, licencia
(`LICENSE`), cita (`CITATION.cff`) y metadatos para Zenodo (`.zenodo.json`).
Solo faltan los pasos que necesitan tus cuentas.

## 1. Subir el código a GitHub

1. Entra en <https://github.com/new>, crea un repositorio **público** llamado
   `OpenMunicipality`, sin README ni licencia (ya vienen incluidos).
2. En una terminal, dentro de esta carpeta (las tres primeras líneas solo
   si la carpeta aún no es un repositorio git, es decir, si no tiene `.git`):

   ```bash
   git init
   git add .
   git commit -m "OpenMunicipality 1.0.0" && git tag v1.0.0
   git remote add origin https://github.com/TU-USUARIO/OpenMunicipality.git
   git branch -M main
   git push -u origin main
   ```

3. En la pestaña **Actions** del repositorio verás que se ejecutan los tests en
   Python 3.10, 3.11, 3.12 y 3.13. Deben salir en verde.
4. Sustituye `USERNAME` por tu usuario en `CITATION.cff` y añade tu ORCID y tu
   afiliación (están marcados con `TODO`).

## 2. Conseguir el DOI en Zenodo

1. Entra en <https://zenodo.org> con tu cuenta de GitHub.
2. En tu perfil, abre **GitHub** y activa el repositorio `OpenMunicipality`.
3. En GitHub, crea una *release*: **Releases → Draft a new release**, etiqueta
   `v1.0.0`, título `OpenMunicipality 1.0.0`, y publícala.
4. Zenodo archiva esa versión y le asigna un DOI en unos minutos. Cópialo en el
   artículo (tabla de metadatos), en `CITATION.cff` y en el README.

## 3. Ponerlo en línea (Streamlit Community Cloud, gratuito)

1. Entra en <https://share.streamlit.io> con tu cuenta de GitHub.
2. **Create app → Deploy a public app from GitHub**.
3. Repositorio `TU-USUARIO/OpenMunicipality`, rama `main`, archivo
   `app.py`. En *Advanced settings* elige Python 3.12.
4. Puedes elegir una dirección propia, por ejemplo
   `openmunicipality.streamlit.app`.
5. Pon esa dirección en el artículo y en el README. El código para insertar el
   panel en otras webs la toma automáticamente.

## 4. Actualizar los datos cada año

- **Opción manual:** descarga de CONPREL los archivos de Access y ejecuta
  `python scripts/build_conprel.py Presupuestos2026.zip …` (necesita
  `mdbtools`).
- **Opción automática:** en GitHub, **Actions → Update official data → Run
  workflow**. Pega los enlaces de descarga de CONPREL y se abrirá una *pull
  request* con los datos nuevos ya probados.
- Cada enero, actualiza `data/conprel/cpi.csv` con la inflación media del año
  anterior que publica el INE.

## 5. Antes de enviar a SoftwareX

- La release de GitHub, el DOI de Zenodo y la versión citada en el artículo
  deben coincidir (`v1.0.0`).
- El repositorio debe ser público en el momento del envío.
