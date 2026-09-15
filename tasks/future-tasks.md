general:

- [x] Decir en agents.md que deben usar conventional commits, sin descripción y concisos.
- [x] busca tunido debe ir todo junto `BuscaTuNido` (no es necesario cambiar el nombre de la org).
- [x] Ver y solucionar los errores y advertencias que biome entrega, tanto en la api y en web.
- [x] Escribir los readme para web y para api. Escrito de forma concisa.
- [x] Añade una configuración en biome (para la api y web) para que el linter emita errores y advertencias más estrictas.

back:

- [x] Poblar la base de datos con datos de prueba usando algoritmos para generar datos aleatorios.
- [x] Implementar la API REST para los servicios (los edpoint deben tener protección por jwt y un usuario solo puede acceder a sus propios datos, el admin puede acceder a todos los datos)
- [x] añadir cientos/miles de datos a la db
- [ ] en la tabla "reviews" el campo imagen debe tener un limite de 3 imágenes en la api. El dto debe rechazar más de 3 imágenes

front:

- [x] Implementar la web en base al front-mockup.png de alto nivel, el front-mockup.png solo contiene 4 paneles, con la minima cantidad de elementos necesarios. El resto de paneles y elementos deben ser creados en base a decisiones típicas de diseño de apps relacionadas.
- [x] Mejorar la ui de la web, analiza todas las fotos dentro de `rediseño/`. La web mobile tiene que tener un diseño más plano y minimalista (tanto en dark mode como en light mode), los colores deben ser reconfortables.
- [x] Mejorar la ux de la web usando una biblioteca de motions para css, para tener interacciones más agradables mobile.
- [x] el mapa debe ser completamente interactivo (te deberías poder moverlo a cualquier lado, hacer zoom, etc.). Usa una biblioteca,el mapa debe ser real y debe leer mi ubicación actual. La app debe pedir acceso a tu ubicación. En el slide de ciudades la primera ciudad debe ser la de tu ubicación actual real. Por defecto el mapa debe estar en la ciudad de tu ubicación actual, al seleccionar una ciudad se debe centrar el mapa en esa ciudad. Al seleccionar una universidad debe aparecer un marcador en el mapa en la ubicación de la universidad. Crea un plan completo de como esto va ser implementado y pregúntame a mi para darte ok o dar una review.
- [ ] Discutir sobre cual es la mejor forma implementar un login para un admin/moderador, sin que un usuario común pueda ver o acceder a esa sección.
- [x] Mejora de ux, actualmente si ya has iniciado sección, y recargas página, te aparece la ventana de login por unos segundos antes de redirigirse a la app. Soluciona este problema, puede ser por medio de algún loader o una solución más elegante.
- [x] Usa el icono adecuado que se encuentra en `referencias/icon`. Ahí está el ícono en diferentes formatos, y uno sin fondo. Usa el icono en diferentes partes de la app.
- [x] Implementar que permita ver las reseñas las pensiones (usa referencias/reseñas).
- [x] Explícame para qué sirve `<script src="/theme-init.js" />` en `src/app/layout.tsx`? y porqué no es `.ts`?
- [x] Búsqueda dinámica de pensiones según la zona explorada en el mapa (ver detalle en `web/tasks/dynamic-map-bounds-search.md`).
- [ ] el componente de estudiante y de dueño deben ser separados. El de dueño debe tener una interfaz diferente (ver plan en `web/tasks/role-based-ui-separation-student-vs-landlord.md`).
- [ ] implementación real de la api, solo para estudiantes y remoción total de mocks (ver plan por Olas en `web/tasks/` desde `Wave 0` hasta `Wave 4`).

## No implementar lo siguiente, aún no hay `referencias/<dir>` para este caso:

- [ ] Mejorar sistema de filtro en la barra de busqueda.
- [ ] Mejorar la lógica de como funciona la barra de búsqueda.
- [ ] Dueño debe tener una interfaz diferente (sin favoritos, sin reseñas, entre otros).
- [ ] Hacer la web compatible con desktop basado en las `referencias/...`.
- [ ] Mejorar pantalla de inicio (login) con imágenes, videos u otros que ayuden a dar a entender de qué va la plataforma.
