# Knowledge Graph Backend

## Descripción
Este proyecto es un backend desarrollado para explorar la red de conocimiento de Wikipedia como un grafo interactivo. Permite a los usuarios visualizar cómo un concepto se conecta con otros, descubriendo relaciones y expandiendo su exploración de forma dinámica.

## Tecnologías Usadas
- **FastAPI**: Framework para construir APIs rápidas y eficientes.
- **MongoDB**: Base de datos NoSQL utilizada para almacenar artículos y exploraciones.
- **wikipedia-api**: Biblioteca para interactuar con la API de Wikipedia.
- **BeautifulSoup**: Utilizada para extraer texto plano de HTML.
- **Uvicorn**: Servidor ASGI para ejecutar la aplicación FastAPI.

## Configuración del Entorno
1. **Clonar el Repositorio**:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd knowledge_graph
   ```

2. **Crear y Activar el Entorno Virtual**:
   ```bash
   python -m venv .env
   .env\Scripts\activate  # En Windows
   source .env/bin/activate  # En macOS/Linux
   ```

3. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Funcionalidades
- **Búsqueda de Artículos**: Permite buscar artículos en Wikipedia y devolver una lista de artículos sugeridos.
- **Exploración del Grafo**: Explora el grafo a partir de un artículo dado, mostrando nodos y aristas.
- **Gestión de Exploraciones**: Guarda y lista exploraciones de artículos.

## Ejecución del Servidor
Para iniciar el servidor, ejecuta el siguiente comando:
```bash
uvicorn app.main:app --reload
```

## Alcance
Este backend está diseñado para integrarse con un frontend que visualiza los datos de manera amigable. Proporciona endpoints para buscar y explorar artículos de Wikipedia, así como para gestionar exploraciones guardadas.