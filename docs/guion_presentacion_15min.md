# Guion de Presentación — 15 minutos (F15)
## II Datathon LoDCOREMadrid · UC3M + Comunidad de Madrid · 29 de octubre de 2026

> **Qué es este documento:** el texto literal para ensayar. Cada bloque indica quién habla, qué
> pantalla tiene abierta, qué hace con el ratón y qué frase clave debe quedar sonando.
> **Idioma:** español de España, institucional.
> **Prohibido en voz alta:** SHAP, ONNX, float32, AVM, p-valor, gradient boosting, "machine learning"
> como magia. **También prohibido:** decir 179 municipios (el piloto son 20), prometer efecto entre
> pueblos vecinos, o decir que todos los datos son oficiales.
> **Cifras que se pueden pronunciar (ninguna más):** 20 municipios, 8 comarcas, 200.267 habitantes,
> 37,9 de índice medio, 12 municipios en alerta, 5.078 personas de cupo, 35,9 M€ de refuerzo.
> **Estado:** v2 (24 oct 2026). Pendiente de ajustar el `nuevo_ica` que muestra el simulador cuando
> se alineen las sensibilidades del optimizador (las cifras de personas y euros no cambian).

---

## 0. Cómo se reparte el turno

| Persona | Rol en la defensa | Bloques que lleva |
|---|---|---|
| **P3** | Narrador y operador del portal | Apertura (00:00), mapa (03:30), cierre (13:00) |
| **P2** | Cómo funciona, qué límites tiene, y operador del simulador | Arquitectura (02:00), simulador (05:30), el tiempo (11:30) |
| **P1** | Los datos y el "dónde invertir" | Simulador (co-explica 05:30), optimizador (08:30) |

**Reglas de oro del turno**
1. Nadie habla más de 3 minutos seguidos: cada bloque tiene un dueño claro.
2. Si una demo falla, se dice en voz alta y se pasa: "esto lo tenemos medido, os lo enseño en un
   segundo" (ver Plan B).
3. Si el jurado pregunta algo que no estáis seguros, la respuesta es: "no lo hemos calculado; es lo
   siguiente que vamos a hacer".
4. Cada bloque cierra con una frase que se pueda repetir en un tweet. No improvisar cifras.

---

## 1. Guion minuto a minuto

### 00:00 – 02:00 · P3 · PANTALLA: Dashboard (APEX, Página 1)
**Acción:** abrir en la vista general. Señalar los cuatro indicadores de arriba sin leerlos uno a uno.

> «Buenos días. Somos el equipo LoDCORE. La pregunta que nos ha hecho la Comunidad de Madrid es
> sencilla de enunciar y difícil de responder: **de qué manera repartimos a la gente que llega a
> Madrid entre los municipios pequeños, sin que se les rompe la sanidad, la escuela o la vivienda**.
>
> Y la respuesta que se escucha siempre, y que no sirve, es "repártanlo por partes iguales".
> Nosotros decimos otra cosa: **no todos los municipios valen lo mismo para alojar gente, y el dinero
> público tiene que ir a donde más gente puede absorber.**
>
> Esto es Madrid: 179 municipios, casi todos por debajo de 50.000 habitantes. Nosotros hemos empezado
> por 20, repartidos por las 8 comarcas, para no enseñarles un mapa bonito sino un diagnóstico
> verificable. En pantalla tienen el índice de capacidad de acogida: verde, ámbar y rojo.
>
> Los cuatro números de arriba: veinte municipios analizados, un índice medio comarcal de 37,9 sobre
> 100, 5.078 personas que esos municipios podrían absorber hoy sin colapsar un solo servicio, y
> 35,9 millones de euros de refuerzo que harían falta para los doce que están en rojo.»

**Frase clave:** «No todos los municipios valen lo mismo, y el dinero tiene que ir donde más gente puede absorber.»
**No decir:** "predicción", "IA", "machine learning". **Decir:** "diagnóstico", "índice", "estimación".

---

### 02:00 – 03:30 · P2 · PANTALLA: Dashboard, luego diapositiva de arquitectura
**Acción:** una diapositiva con 4 cajas: *Datos oficiales → Índice y reglas → Base de datos Oracle → Portal*.

> «Para que el jurado pueda valorarlo, os cuento en un minuto cómo está construido y, sobre todo,
> qué es verdad y qué es estimación.
>
> Primero, lo que es verdad. La población de cada municipio viene del padrón oficial del Instituto
> Nacional de Estadística, descargado del propio INE y guardado con fecha. Y los recuentos de centros
> de salud y de centros educativos vienen del portal de datos abiertos de la Comunidad de Madrid,
> también descargados y guardados con fecha. Todo eso se puede auditar: en el repositorio está de
> dónde salió cada número y cuándo.
>
> Segundo, lo que aún es estimación. La dotación de médicos por municipio, las plazas escolares y los
> precios están calibrados con un modelo de referencia, no leídos de un registro oficial. Lo decimos
> porque es justo: hoy enseñamos a escala y con datos trazados; el paso siguiente es conectar el
> registro sanitario y el de la Consejería de Educación, y eso ya está planificado.
>
> Tercero, cómo decidimos. Aquí no hay una caja negra que diga "este municipio es bueno". Hay un índice
> de 0 a 100 con cuatro componentes —sanidad, educación, conectividad, vivienda y holgura— y encima
> una regla dura: **si un municipio rebasa un umbral de saturación en sanidad o en escuela, su nota
> baja y se queda baja, por muy buena que sea su vivienda o su suelo.** Nadie compensa un servicio
> roto con un terreno barato. Eso es lo que hace que el diagnóstico sirva para decidir.
>
> Y todo el cálculo se ejecuta dentro de la base de datos de Oracle; el portal solo lo cuenta.»

**Frase clave:** «Si un servicio está roto, nada lo compensa: ni el suelo ni el precio.»
**Transparencia (no saltarse esto):** es el bloque donde decís qué datos son oficiales y cuáles no.

---

### 03:30 – 05:30 · P3 · PANTALLA: Mapa semafórico (APEX, Página 1 con mapa)
**Acción:** filtrar por "en alerta"; pasar el ratón por 3 fichas (Robledo, Navalcarnero, Ciempozuelos).

> «Este es el mapa. Cada punto es un municipio, y el color es su diagnóstico: verde puede absorber
> gente hoy, ámbar puede con un esfuerzo razonable, rojo no puede sin inversión previa.
>
> Fijaos en el patrón, que es la información útil. De los veinte municipios analizados, **diez están
> bloqueados por la sanidad** —más habitantes de los que puede atender un médico— y **nueve por la
> educación**, con las aulas por encima del 95 % de ocupación. Solo uno, Buitrago del Lozoya, tiene la
> vivienda como cuello de botella.
>
> Y un detalle que a nosotros nos costó una discusión y que creed que importa: el municipio con mejor
> nota del mapa, Robledo de Chavela, no es el más grande ni el más caro. Tiene 4.818 habitantes, un
> centro de salud para cada 803 vecinos y aulas al 75 %. Su nota es un 66,7 sobre 100.
>
> En el otro extremo, Navalcarnero: 33.331 personas, más de 1.600 habitantes por médico y las aulas al
> 95 %. Su nota es un 24,5. No es que sea un mal sitio: es que hoy no puede absorber a nadie más.»

**Frase clave:** «Diez municipios están bloqueados por la sanidad y nueve por la educación: el mapa dice dónde hay que invertir.»

---

### 05:30 – 08:30 · DEMO 1 (P2 opera, P1 explica) · PANTALLA: Ficha municipal + simulador
**Acción:** abrir Chinchón (nota 49,5; 5.800 habitantes; 578 personas de cupo). P2 mete +400 vecinos y le da a simular.

> **P2:** «Voy a hacer la pregunta que se hará un alcalde: si a este municipio le llegaran 400 vecinos
> nuevos, ¿qué pasa? Ni un cálculo hecho a mano: le doy a "simular" y la herramienta me dice qué
> servicio se rompe primero y qué dinero hace falta para evitarlo.»
>
> **P1 (mientras se ve el resultado):** «Esto es lo importante: el simulador no nos dice "va a haber
> más tensión". Nos dice **qué servicio se satura primero**. Si el primer límite es la vivienda, no hay
> dinero que lo arregle; si es la sanidad, el número de médicos que hay que contratar; si es la
> escuela, las plazas que hay que crear. Y nos da el coste, con un precio por médico y un precio por
> plaza que están a la vista y se pueden cambiar por el gestor.
>
> Y hay un segundo paso, que es el que de verdad responde a la pregunta del reto: **si en lugar de
> mirar un municipio miramos una comarca y tenemos una partida cerrada, ¿en qué municipios concretos
> la gastamos?** Eso es lo que enseño en un minuto, pero antes, un aviso sobre lo que veis: si un
> municipio tiene la vivienda como techo, el simulador lo dirá. Y dirá que no hay inversión que valga,
> porque no es un problema de dinero.»

**Frase clave (P1):** «No dice "habrá más tensión": dice qué servicio se rompe primero y cuánto cuesta evitarlo.»
**Si el simulador tarda:** no esperéis en silencio. P1 explica la lógica mientras carga.
**Números que hay que tener a mano (leídos de la pantalla, no memorizados):** Chinchón: 5.800 hab.,
nota 49,5, cupo 578 personas, límite educación, 1.160 hab./médico, 84 % de ocupación.

---

### 08:30 – 11:30 · DEMO 2 (P1 opera y explica) · PANTALLA: Tabla de asignación del optimizador
**Acción:** abrir el optimizador. Comarca: **Sierra Oeste**. Presupuesto: **2.000.000 €**. Leer la asignación en voz alta.

> **P1:** «Aquí está el corazón del proyecto. El gestor comarcal tiene una partida cerrada —pongamos
> dos millones de euros— y tiene que decidir en qué municipios concretos se la gasta. Nuestra
> herramienta responde.
>
> Miren la primera fila: Villa del Prado. Su nota es un 36,9 y su cuello de botella es la sanidad:
> 1.549 habitantes por médico, justo en el límite. Le asignamos **un médico de más, 450.000 euros**,
> y con ese solo cambio el municipio pasa a poder absorber **830 personas más** sin colapsarse.
>
> Segunda fila: San Martín de Valdeiglesias. Ahí el límite son las aulas, y le asignamos **50 plazas
> escolares, 600.000 euros**, que libera **279 personas** de cupo.
>
> Tercera: Robledo de Chavela, 50 plazas más, **600.000 euros**, y **227 personas** más de cupo.
>
> En total: **1.650.000 euros de los dos millones, 1.336 personas más de acogida en la comarca**, y
> 350.000 euros sin gastar, porque ninguna otra inversión de la comarca superaba el listón. Eso último
> es tan importante como lo otro: **la herramienta también sabe decir "aquí no hay que gastar".**
>
> Y ahora el ejemplo que más nos gusta, porque es el que un algoritmo sin criterio arruinaría.
> Navalcarnero, la comarca Sur: le ponemos dos millones de euros y **la herramienta no gasta ni uno**.
> ¿Por qué? Porque su límite no es el dinero: es que no hay vivienda vacía ni suelo donde alojar a más
> vecinos. Blindar su sanidad no aumenta la acogida de nadie. Un modelo que solo buscase "gastar el
> presupuesto" le habría recomendado meter millones ahí. El nuestro se niega, y dice: primero
> vivienda, después servicios.
>
> Esto no es el futuro: hoy funciona, está escrito, se puede auditar y se puede cambiar el precio del
> médico o de la plaza con un solo parámetro.»

**Frase clave:** «Dos millones, tres municipios, 1.336 personas más de cupo — y 350.000 euros que la herramienta decide no gastar.»
**Cifras exactas del guion (verificadas):** 1 médico en Villa del Prado = 450.000 € = +830 personas;
50 plazas en San Martín = 600.000 € = +279; 50 plazas en Robledo = 600.000 € = +227; total 1.650.000 €,
remanente 350.000 €, +1.336 personas; Navalcarnero = 0 €.
**Si preguntan "es óptimo":** «Es una heurística voraz: no es un óptimo matemático, es una asignación
viable y auditable, y lo decimos así en la documentación.»

---

### 11:30 – 13:00 · P2 · PANTALLA: Ficha con proyección a 2030/2035
**Acción:** abrir la ficha de Ciempozuelos o Navalcarnero (nota 25,3; saturación en 2025).

> «Y ahora la pregunta que siempre aparece: ¿esto aguanta mañana? Porque un diagnóstico que solo vale
> para hoy no sirve para invertir.
>
> En la ficha de cada municipio tienes la proyección de población a 2027, 2029 y 2031, con una
> horquilla de incertidumbre. Para el conjunto de los veinte municipios, el modelo resume el salto
> de 200.267 habitantes hoy a 216.597 en 2030 y 234.336 en 2035: casi 35.000 personas más en una
> década.
>
> Y de ahí sale la fecha que a un alcalde le importa: **el año en que el municipio se satura si no se
> invierte**. Ciempozuelos, 26.350 habitantes, aulas al 96 %: saturación en 2025. Navalcarnero, también
> 2025. En total, doce municipios de los veinte necesitan refuerzo ya. No es una previsión lejana: es
> una factura de este año.
>
> Esta es la parte que menos nos gusta, y por eso la ponemos delante: el modelo tiene fecha de
> caducidad y lacial.»

**Frase clave:** «Doce de veinte municipios necesitan refuerzo ya: esto no es una previsión lejana, es una factura de este año.»
**No decir:** "confianza del 95 %" como si fuera un dato de mercado; decirlo como "horquilla de
incertidumbre" y, si insisten, "calculada por bootstrap de municipios".

---

### 13:00 – 15:00 · P3 · PANTALLA: Dashboard + vista de "Fuentes oficiales"
**Acción:** volver al dashboard; mostrar la vista de fuentes con fechas de descarga.

> «Cerramos con tres cosas.
>
> La primera, qué os lleváis. No es un mapa de precios ni un ranking de municipios bonitos. Es una
> herramienta de decisión: dónde están los cuellos de botella, cuánto dinero cuesta cada uno y qué
> parte de una partida cerrada maximiza la gente que una comarca puede absorber. Todo con la fuente de
> cada dato a la vista y con fecha: eso se lo exigimos nosotros, porque una administración no puede
> tomar una decisión de inversión con un número del que no sabe de dónde sale.
>
> La segunda, lo que aún no tenemos, y lo decimos nosotros. Hemos trabajado con veinte municipios de
> los 179, con la dotación de médicos y plazas estimada y sin el efecto entre pueblos vecinos, que es
> la siguiente fase. La conexión con los registros oficiales de sanidad y educación, y el modelo de
> difusión comarcal, están planificados y son el siguiente paso, no una promesa de hoy.
>
> Y la tercera, qué pedimos. Pedimos acceso a los datos de dotación reales de la Comunidad de Madrid
> y del Instituto Nacional de Estadística, para sustituir las estimaciones por registros oficiales.
> Con eso, esta misma herramienta pasa de ser un diagnóstico de veinte municipios a ser el soporte de
> la planificación de los ciento sesenta municipios pequeños de la región.
>
> Gracias. Si queréis, os enseñamos cómo se usa con un presupuesto real de vuestra comarca.»

**Frase clave:** «No es un ranking de municipios bonitos: es una herramienta para decidir dónde invertir.»
**Última frase (mirada al jurado):** «Gracias. El siguiente paso es sustituir estimaciones por registros oficiales.»

---

## 2. Plan B (si algo falla en la demo)

| Fallo | Qué hace quien está delante | Frase de recurso |
|---|---|---|
| La web de APEX no carga | P3 salta a la tabla de asignación (o al portal local `frontend/index.html`) | «Os enseño el resultado en tabla, que es lo mismo.» |
| El simulador tarda | P1 explica la lógica mientras carga; P2 tiene la cifra de Chinchón anotada (578 de cupo, 1.160 hab./médico, 84 % aulas) | «Mientras carga, os explico qué está calculando.» |
| El optimizador no responde | P1 tiene en una diapositiva la foto de la tabla de Sierra Oeste | «Teníamos la tabla del último ejercicio; es esta.» |
| Se pierde la red | P3 abre `frontend/index.html` (portal offline con datos embebidos) | «Esto es la versión offline que usamos para ensayar.» |
| Se pregunta por un municipio que no está | P1: «Está en la ampliación a 160 municipios, que es el siguiente paso.» | Nunca inventar un dato. |

---

## 3. Preguntas del jurado y respuesta preparada

**1. «¿Los datos son reales?»**
«La población viene del padrón oficial del INE y los recuentos de centros del portal de datos abiertos
de la Comunidad de Madrid, descargados y fechados: se puede auditar. La dotación de médicos y plazas
y los precios son estimaciones calibradas y lo decimos en la propia ficha. Conectar el registro
oficial de sanidad y educación es el siguiente paso que pedimos.»

**2. «¿Por qué 20 municipios y no los 179? ¿No es una muestra sesgada?»**
«Es un piloto deliberado: 20 municipios y 8 comarcas, con reproducibilidad en minutos. La escalabilidad
está probada: el mismo proceso se aplica a los municipios menores de 50.000 habitantes (~160) cuando
conectemos las fuentes oficiales. Publicamos además el procedimiento completo, no solo el resultado.»

**3. «¿Cómo evitáis que el sistema diga que un municipio es bueno solo porque es barato?»**
«Por una regla dura: si el municipio rebasa el umbral de saturación sanitaria o educativa, su nota
queda truncada en "alerta" por muy buena que sea su vivienda, su suelo o su precio. El precio entra en
el índice con peso, pero no rescata. Es la diferencia entre un ranking y un diagnóstico de capacidad de
acogida.»

**4. «¿Qué pasa con los doce municipios en alerta?»**
«Hoy sabemos lo que cuesta: 35,9 millones de euros de refuerzo. Y sabemos qué parte de esa partida se
puede filtrar con mejor retorno: es lo que hace el optimizador. El resto depende de decisiones de
política de inversión que corresponden a los gestores públicos, no a nosotros.»

**5. «¿Y el efecto en los pueblos vecinos? Lo has mencionado en la web.»**
«No, y no lo prometemos. Hoy la asignación se hace dentro de una comarca repartiendo una partida
compartida. El modelo de difusión continua entre municipios —con matrices de movilidad— es la fase 2
del proyecto, y está identificado como tal.»

**6. «¿El precio por metro cuadrado es fiable?»**
«No es una valoración: es un estimador de orden de magnitud para valorar la asequibilidad. Con veinte
municipios, nuestro estimador se equivoca de media en unos 380 euros por metro cuadrado cuando cambia
el municipio, así que lo usamos para comparar acceso, no para tasar. Está declarado como tal en la
documentación técnica.»

**7. «¿Quién lo usaría y para qué?»**
«Dos perfiles. La administración comarcal y los ayuntamientos, para ordenar la inversión en
dotaciones; y las familias, para encontrar el municipio que encaja con su presupuesto y con su perfil.
La misma ficha sirve a los dos: a unos les dice dónde invertir, a otros les dice dónde vivir.»

---

## 4. Checklist del ensayo (antes del 28 por la noche)

- [ ] Ensayo cronometrado ×3: 15:00 ± 0:30. Si se pasa, se recorta el bloque 11:30 (proyección).
- [ ] Cada persona dice su bloque **de memoria**: nadie lee de la pantalla.
- [ ] P2 tiene abierto y en marcha el simulador con Chinchón cargado; P1, el optimizador con 2 M€ y Sierra Oeste.
- [ ] P3 tiene la vista de fuentes preparada (para el cierre y para la pregunta 1).
- [ ] Tabla de respaldo en una diapositiva (foto de la asignación de Sierra Oeste).
- [ ] Comprobar que nadie dice: SHAP, ONNX, float32, AVM, "machine learning", "179", "predictivo".
- [ ] Comprobar que "5.078" y "35,9 M€" coinciden con la pantalla en cada ensayo.
- [ ] Ensayo en el ordenador del salón (29 oct por la mañana): mismos navegadores, misma red, presentación en local.
- [ ] Dejar en el repositorio y accesible desde el móvil del presentador: datos, informe de validación y este guion.
