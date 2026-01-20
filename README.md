# 🏙️ Análisis de Mercado Inmobiliario - Capital Federal, Argentina

---

## 📑 Índice de Contenidos

*   [📂 Estructura del Proyecto](#-estructura-del-proyecto)
*   [🕷️ Componente 1: El Scraper](#️-componente-1-el-scraper-srcscraperpy)
    *   [🛠️ Tecnologías y Librerías](#️-tecnologías-y-librerías)
    *   [🧠 Lógica de Funcionamiento](#-lógica-de-funcionamiento)
    *   [🚀 Uso del Scraper](#-uso-del-scraper)
*   [📊 Componente 2: Análisis y Modelado](#-componente-2-análisis-y-modelado-notebooksanalisisipynb)
    *   [1. Limpieza y Procesamiento de Datos](#1-limpieza-y-procesamiento-de-datos)
    *   [2. Feature Engineering](#2-feature-engineering-ingeniería-de-características)
    *   [3. Análisis Exploratorio (EDA)](#3-análisis-exploratorio-eda)
    *   [4. Modelado Estadístico](#4-modelado-estadístico)
*   [💡 Key Insights: Hallazgos Principales](#-key-insights-hallazgos-principales)
    *   [📈 Disparidad de Precios por Barrio](#-disparidad-de-precios-por-barrio)
    *   [🧠 Interpretación de Coeficientes](#-interpretación-de-coeficientes-modelo-log-lin)
    *   [📐 El Impacto de las Características Físicas](#-el-impacto-de-las-características-físicas)
    *   [🔍 Análisis de Residuos](#-análisis-de-residuos)
    *   [🎯 Precios Predichos vs. Reales](#-precios-predichos-vs-reales)
    *   [🏆 Desempeño del Modelo](#-desempeño-del-modelo)
*   [📦 Instalación](#-instalación)
*   [📝 Requisitos](#-requisitos)
*   [⚠️ Disclaimer Legal](#️-disclaimer-legal)
## 📂 Estructura del Proyecto

- **`src/`**: Contiene el código fuente del scraper (`scraper.py`).
- **`notebooks/`**: Contiene los Jupyter Notebooks para el análisis de datos (`analisis.ipynb`).
- **`data/`**: Directorio destinado al almacenamiento de datasets (crudos y procesados).
- **`requirements.txt`**: Lista de dependencias del proyecto.

---

## 🕷️ Componente 1: El Scraper (`src/scraper.py`)

El módulo de scraping está diseñado para recolectar datos de publicaciones de venta de departamentos en **ZonaProp**, uno de los portales inmobiliarios más grandes de Argentina.

### 🛠️ Tecnologías y Librerías
*   **`cloudscraper`**: Se utiliza en lugar de la librería estándar `requests` para evadir las protecciones anti-bot de Cloudflare (errores 403/Forbidden) que frecuentemente bloquean scrappers sencillos.
*   **`BeautifulSoup` (bs4)**: Utilizada para el parseo del HTML y la extracción de información estructurada del DOM de la página.
*   **`pandas`**: Para estructurar los datos recolectados en un DataFrame y exportarlos a CSV.
*   **`argparse`**: Para permitir la ejecución del script desde la línea de comandos con parámetros personalizados.

### 🧠 Lógica de Funcionamiento
El script define una clase principal `ZonaPropScraper` que encapsula la lógica de extracción:
1.  **Navegación Robusta**: Itera a través de las páginas de listados (`-pagina-{n}.html`), construyendo dinámicamente las URLs.
2.  **Simulación Humana**: Implementa pausas aleatorias (`time.sleep(random.uniform(3, 7))`) entre peticiones para evitar ser bloqueado por realizar demasiadas solicitudes en poco tiempo.
3.  **Extracción de Datos**: Para cada propiedad listada, extrae:
    *   **Precio**: Valor en USD o ARS.
    *   **Ubicación**: Barrio y dirección aproximada.
    *   **Características**: M² totales, cantidad de ambientes, dormitorios, baños (parseados desde tags específicos).
    *   **Expensas**: Costos de mantenimiento mensual.
    *   **Descripción y URLs**: Texto descriptivo y link a la publicación original.
4.  **Manejo de Errores**: Incluye bloques `try-except` para manejar fallos en la conexión o cambios en la estructura del HTML sin detener la ejecución total.

### 🚀 Uso del Scraper
Para ejecutar el scraper y obtener, por ejemplo, 100 propiedades:
```bash
python src/scraper.py --qty 100
```
Si se ejecuta sin argumentos (o con 0), intentará scrapear el máximo posible hasta encontrar un límite de seguridad.

---

## 📊 Componente 2: Análisis y Modelado (`notebooks/analisis.ipynb`)

El notebook principal realiza un trabajo exhaustivo de limpieza, ingeniería de features y análisis estadístico.

### 1. Limpieza y Procesamiento de Datos
Dado que los datos web suelen ser "sucios", esta etapa es crítica:
*   **Parsing con Regex**: Se utilizan expresiones regulares (`re`) para extraer valores numéricos de columnas de texto libre como `features` (ej: transformar "60 m² tot." a `60` int).
*   **Normalización**: Conversión exhaustiva de precios y superficies.
*   **Manejo de Nulos**: Imputación o eliminación de registros incompletos que podrían afectar el modelado.

### 2. Feature Engineering (Ingeniería de Características)
Se crean nuevas variables para enriquecer el análisis:
*   **`precio_m2`**: Variable fundamental para comparar valores relativos entre barrios.
*   **`ambientes_m2`**: Proxy de la distribución/amplitud de los espacios.
*   **`barrio`**: Extracción limpia del barrio desde la cadena de ubicación para permitir agrupaciones geográficas.

### 3. Análisis Exploratorio (EDA)
*   **Detección de Outliers**: Se utilizan **Boxplots** y técnicas estadísticas (Rango Intercuartil) para identificar y filtrar propiedades con precios o superficies anómalas (ej: errores de carga com "USD 1" o mansiones que distorsionan el promedio).
*   **Distribuciones**: Visualización de cómo se distribuyen los precios y superficies en la capital.

### 4. Modelado Estadístico
El notebook avanza hacia inferencia estadística utilizando **`statsmodels`**:
*   **Regresión OLS (Ordinary Least Squares)**: Se ajustan modelos lineales para estimar el impacto de cada variable (m2, cochera, ubicación) en el precio final.
*   **Diagnóstico**: Análisis de coeficientes, valores-p (significancia estadística) y bondad de ajuste ($R^2$) para validar las hipótesis del mercado.

---

## � Key Insights: Hallazgos Principales

### 📈 Disparidad de Precios por Barrio
El análisis de regresión múltiple (Log-Lin con variables dummy por barrio) reveló disparidades significativas en las valuaciones inmobiliarias, manteniendo constantes otras variables como la superficie:
*   **Intercepto**: 
    *   La constante del modelo representa el valor base de una unidad en el barrio de referencia (Abasto), a partir de la cual se aplican los premios y descuentos por características ('m2', 'baños', 'ambientes', 'cocheras') y ubicación.
*   **🤑 El Más Caro: Puerto Madero**:
    *   Este barrio presentó el coeficiente positivo más alto del modelo (`0.8241`).
    *   **Interpretación**: Una propiedad en Puerto Madero cuesta aproximadamente un **128% más** que el barrio Abasto (ajustado por otras variables), *ceteris paribus*. Es, por lejos, el outlier más significativo del mercado.
*   **💎 Zona Premium**: Barrios como **Palermo Chico** (Coef `0.625`) y **Palermo Nuevo** (Coef `0.550`) también muestran valuaciones muy por encima de la media, consolidándose como submercados de lujo.
*   **📉 Barrios Más Accesibles**: En el otro extremo, **Villa Soldati** (Coef `-0.7736`) y **Pompeya** (Coef `-0.7894`) muestran los descuentos más fuertes respecto a la media, con precios ajustados aproximadamente un **50-55% por debajo** del valor de referencia.
![Precios Promedio por Barrio](/screens/Precios%20Promedios%20Más%20Caros%20por%20Barrios.png)
![Precios Promedio por Barrio](/screens/Precios%20Promedios%20Más%20Baratos%20por%20Barrios.png)

### 🧠 Interpretación de Coeficientes (Modelo Log-Lin)
Dado que la variable dependiente es el logaritmo del precio (`log_precio`), la interpretación de los coeficientes ($\beta$) para las variables binarias (dummies) no es directa. Se calcula el impacto porcentual exacto con la fórmula:
$$ \% \Delta = (e^{\beta} - 1) \times 100 $$

**Ejemplo: Valor Marginal de una Cochera**
*   **Coeficiente**: `0.2299`
*   **Cálculo**: $e^{0.2299} - 1 \approx 0.258$
*   **Conclusión**: *Ceteris paribus* (manteniendo todo lo demás constante), disponer de una cochera incrementa el valor de la propiedad en un **25.8%** en promedio.

### 📐 El Impacto de las Características Físicas
Más allá de la ubicación, las características intrínsecas de la propiedad juegan un rol crucial validado por el modelo:
*   **Superficie (m²)**: Es el predictor individual más fuerte.
*   **Baños**: Coeficiente `0.2727`.
*   **Cocheras**: Coeficiente `0.2299`.

### 🔍 Análisis de Residuos
Se realizaron pruebas estadísticas para verificar la normalidad de los errores del modelo:
*   **Diagnóstico**: Los tests **Omnibus** y **Jarque-Bera** arrojaron p-valores de `0.000`, rechazando la hipótesis nula de normalidad perfecta.
*   **Asimetría (Skewness)**: `-0.165`. Indica una ligera asimetría negativa.
*   **Curtosis**: `4.348`. Indica una distribución leptocúrtica ("colas pesadas"), señalando la presencia de outliers de precio que el modelo no logra capturar totalmente.
*   **Validación**: A pesar de la falta de normalidad estricta, el gran tamaño de la muestra ($N=8598$) garantiza la validez asintótica de las inferencias estadísticas, permitiendo confiar en la significancia de los co  eficientes.
![Residuos vs Valores Ajustados](/screens/Residuos%20vs%20Valores%20Ajustados.png)
![Residuos vs Valores Ajustados](/screens/Q-Q%20plot%20y%20distribucion%20de%20residuos.png)

### 🎯 Precios Predichos vs. Reales
*   El análisis visual comparando los valores predichos por el modelo contra los precios reales de mercado muestra una fuerte concentración alrededor de la línea de identidad ($y=x$).
*   Esto confirma que el modelo no presenta sesgos sistemáticos graves en la mayor parte del rango de precios, aunque la varianza de los residuos aumenta ligeramente en propiedades de valores extremos (heterocedasticidad controlada con HC3).
![Predichos vs Reales](/screens/Precios%20Reales%20vs%20Precios%20Predichos.png)

### 🏆 Desempeño del Modelo
*   **Bondad de Ajuste ($R^2$)**: El modelo explica el **79% de la varianza de los precios**. Se destaca que el 21% restante podría atribuirse a variables no capturadas por la fuente de datos (estado de conservación del edificio, luminosidad, antigüedad exacta o disposición frente/contrafrente).
*   **Robustez**: Se utilizaron errores estándar robustos (**HC3**) durante el ajuste del modelo OLS. Esto corrige la estimación de la varianza de los coeficientes ante la presencia de heterocedasticidad, asegurando que los p-valores y la significancia estadística reportada para cada barrio sean válidas.

---

## �📦 Instalación

1.  Clonar el repositorio.
2.  Crear un entorno virtual (recomendado):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .venv\Scripts\activate
    ```
3.  Instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## 📝 Requisitos
*   Python 3.8+
*   Ver `requirements.txt` para versiones específicas de librerías (`pandas`, `numpy`, `seaborn`, `cloudscraper`, `statsmodels`).

---

## ⚠️ Disclaimer Legal

Este proyecto ha sido desarrollado exclusivamente con fines educativos y académicos. La información y los análisis presentados no constituyen asesoramiento financiero, inmobiliario ni de inversión. Los datos fueron extraídos de fuentes públicas para demostrar técnicas de ciencia de datos y no se garantiza su exactitud, integridad o actualidad para la toma de decisiones comerciales.
