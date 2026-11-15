# Cañón Parabólico - Simulador de tiro parabólico
# Flores Marcos - Lógica de Programación (CESUN)
#
# Versión integrada: el juego del cañón + música de fondo
# + fondo synthwave (atardecer) con todo en estilo neón.
#
# Controles:
#   Flecha arriba / abajo     -> cambia el ángulo del cañón
#   Flecha derecha / izquierda -> cambia la velocidad del disparo
#   Espacio                   -> dispara
#   R                         -> nuevo objetivo
#   Clic en Reproducir/Detener -> prende o apaga la música
#   Esc                       -> salir

import math
import random
import pygame

# ---------- Configuración (diccionario con los valores fijos) ----------
CONFIG = {
    "ancho": 1280,
    "alto": 720,
    "fps": 60,
    "gravedad": 9.8,
    "escala": 10,          # pixeles por metro, para que se vea bien en pantalla
    "suelo": 660,          # altura (en Y) donde está el piso
}

# ---------- Colores (tuplas RGB) ----------
# NUEVO: paleta neón para que combine con el fondo synthwave
ROSA = (255, 0, 200)
CIAN = (0, 240, 255)
AMARILLO = (255, 220, 60)
NARANJA = (255, 140, 60)
MORADO_OSCURO = (15, 0, 35)

COLOR_SUELO = MORADO_OSCURO
COLOR_CANON = CIAN
COLOR_BALA = AMARILLO
COLOR_OBJETIVO = ROSA
COLOR_TEXTO = CIAN
COLOR_TRAYECTORIA = AMARILLO

# ---------- Estado del juego (variables que cambian) ----------
POS_CANON = (120, CONFIG["suelo"])   # base del cañón
LARGO_CANON = 70

# NUEVO: archivos de Media
FONDO = "Media/img1_synthwave.png"
MUSICA = "Media/musica.mp3"

# NUEVO: botones de música (chicos, en la esquina para no tapar el juego)
BOTON_PLAY = pygame.Rect(CONFIG["ancho"] - 340, 20, 150, 45)
BOTON_STOP = pygame.Rect(CONFIG["ancho"] - 175, 20, 150, 45)


def cargar_fondo():
    """NUEVO: carga la imagen del atardecer y la ajusta al tamaño de la ventana."""
    img = pygame.image.load(FONDO).convert()
    return pygame.transform.scale(img, (CONFIG["ancho"], CONFIG["alto"]))


def brillo(screen, color, dibujar):
    """NUEVO: efecto neón. Dibuja lo mismo en una capa transparente, más grueso,
    para que parezca que brilla, y luego encima la versión normal."""
    capa = pygame.Surface((CONFIG["ancho"], CONFIG["alto"]), pygame.SRCALPHA)
    dibujar(capa, (*color, 70), 6)    # versión gruesa y transparente (el resplandor)
    screen.blit(capa, (0, 0))
    dibujar(screen, color, 0)         # versión normal encima


def texto_neon(screen, fuente, texto, color, pos):
    """NUEVO: texto con una sombra rosa detrás para que se vea tipo neón."""
    sombra = fuente.render(texto, True, ROSA)
    screen.blit(sombra, (pos[0] + 2, pos[1] + 2))
    screen.blit(fuente.render(texto, True, color), pos)


def nuevo_objetivo():
    """Regresa un objetivo en una posición aleatoria sobre el suelo."""
    x = random.randint(500, CONFIG["ancho"] - 80)
    radio = 25
    return {"x": x, "y": CONFIG["suelo"] - radio, "radio": radio}


def punta_canon(angulo):
    """Calcula dónde termina el tubo del cañón según el ángulo."""
    rad = math.radians(angulo)
    x = POS_CANON[0] + LARGO_CANON * math.cos(rad)
    y = POS_CANON[1] - LARGO_CANON * math.sin(rad)
    return (x, y)


def disparar(angulo, velocidad):
    """Crea un proyectil con su velocidad descompuesta en X y Y."""
    rad = math.radians(angulo)
    x, y = punta_canon(angulo)
    return {
        "x": x,
        "y": y,
        "vx": velocidad * math.cos(rad),
        "vy": -velocidad * math.sin(rad),   # negativo porque en pantalla Y crece hacia abajo
        "rastro": [],
    }


def actualizar_proyectil(bala, dt):
    """Mueve la bala un paso usando las fórmulas del tiro parabólico."""
    bala["vy"] += CONFIG["gravedad"] * dt
    bala["x"] += bala["vx"] * dt * CONFIG["escala"]
    bala["y"] += bala["vy"] * dt * CONFIG["escala"]
    bala["rastro"].append((int(bala["x"]), int(bala["y"])))


def hay_colision(bala, objetivo):
    """Checa si la bala tocó el objetivo (distancia entre centros)."""
    dx = bala["x"] - objetivo["x"]
    dy = bala["y"] - objetivo["y"]
    distancia = math.sqrt(dx * dx + dy * dy)
    return distancia <= objetivo["radio"] + 6


def fuera_de_pantalla(bala):
    return (bala["x"] > CONFIG["ancho"] + 50
            or bala["x"] < -50
            or bala["y"] > CONFIG["suelo"] + 10)


def dibujar_botones(screen, fuente):
    """NUEVO: botones neón para prender y apagar la música."""
    for boton, texto, color in [(BOTON_PLAY, "Reproducir", CIAN), (BOTON_STOP, "Detener", ROSA)]:
        pygame.draw.rect(screen, MORADO_OSCURO, boton, border_radius=8)
        brillo(screen, color, lambda sup, c, extra: pygame.draw.rect(
            sup, c, boton.inflate(extra * 2, extra * 2), 3 + extra, border_radius=8))
        txt = fuente.render(texto, True, color)
        screen.blit(txt, txt.get_rect(center=boton.center))


def dibujar_escena(screen, fuente, fondo, angulo, velocidad, objetivo, bala, puntos, disparos, mensaje):
    # NUEVO: en vez de un color liso, la imagen del atardecer
    screen.blit(fondo, (0, 0))

    # suelo: oscuro con una línea neón arriba
    pygame.draw.rect(screen, COLOR_SUELO,
                     (0, CONFIG["suelo"], CONFIG["ancho"], CONFIG["alto"] - CONFIG["suelo"]))
    brillo(screen, ROSA, lambda sup, c, extra: pygame.draw.line(
        sup, c, (0, CONFIG["suelo"]), (CONFIG["ancho"], CONFIG["suelo"]), 3 + extra))

    # objetivo: aro neón rosa con centro amarillo
    centro = (objetivo["x"], objetivo["y"])
    brillo(screen, COLOR_OBJETIVO, lambda sup, c, extra: pygame.draw.circle(
        sup, c, centro, objetivo["radio"] + extra, 4 + extra))
    pygame.draw.circle(screen, AMARILLO, centro, objetivo["radio"] // 3)

    # cañón (base + tubo) en cian
    pygame.draw.circle(screen, MORADO_OSCURO, POS_CANON, 22)
    brillo(screen, COLOR_CANON, lambda sup, c, extra: pygame.draw.circle(
        sup, c, POS_CANON, 22 + extra, 4 + extra))
    brillo(screen, COLOR_CANON, lambda sup, c, extra: pygame.draw.line(
        sup, c, POS_CANON, punta_canon(angulo), 10 + extra))

    # trayectoria y bala
    if bala is not None:
        if len(bala["rastro"]) > 1:
            brillo(screen, COLOR_TRAYECTORIA, lambda sup, c, extra: pygame.draw.lines(
                sup, c, False, bala["rastro"], 2 + extra))
        brillo(screen, COLOR_BALA, lambda sup, c, extra: pygame.draw.circle(
            sup, c, (int(bala["x"]), int(bala["y"])), 7 + extra))

    # texto de info
    lineas = [
        f"Angulo: {angulo} grados   (flechas arriba/abajo)",
        f"Velocidad: {velocidad} m/s   (flechas izq/der)",
        f"Puntos: {puntos}   Disparos: {disparos}",
        "Espacio = disparar   R = nuevo objetivo   Esc = salir",
    ]
    y = 20
    for linea in lineas:
        texto_neon(screen, fuente, linea, COLOR_TEXTO, (20, y))
        y += 30

    if mensaje:
        ancho_txt = fuente.size(mensaje)[0]
        texto_neon(screen, fuente, mensaje, AMARILLO, (CONFIG["ancho"] // 2 - ancho_txt // 2, 160))

    dibujar_botones(screen, fuente)


def main():
    pygame.init()
    pygame.mixer.init()   # NUEVO
    screen = pygame.display.set_mode((CONFIG["ancho"], CONFIG["alto"]))
    pygame.display.set_caption("Cañón Parabólico")
    clock = pygame.time.Clock()
    # NUEVO: letra tipo retro (si la Mac no tiene Menlo, usa otra monoespaciada)
    fuente = pygame.font.SysFont("menlo,couriernew,monospace", 20, bold=True)

    # NUEVO: música que empieza sola y se repite
    pygame.mixer.music.load(MUSICA)
    pygame.mixer.music.play(-1)

    # NUEVO: fondo del atardecer
    fondo = cargar_fondo()

    angulo = 45
    velocidad = 60
    objetivo = nuevo_objetivo()
    bala = None
    puntos = 0
    disparos = 0
    mensaje = ""
    tiempo_mensaje = 0

    running = True
    while running:
        dt = clock.tick(CONFIG["fps"]) / 1000.0   # segundos que pasaron desde el frame anterior

        # ----- eventos -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and bala is None:
                    bala = disparar(angulo, velocidad)
                    disparos += 1
                    mensaje = ""
                elif event.key == pygame.K_r:
                    objetivo = nuevo_objetivo()
                    bala = None
                    mensaje = ""
            # NUEVO: clic en los botones de música
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if BOTON_PLAY.collidepoint(event.pos):
                    pygame.mixer.music.play(-1)
                if BOTON_STOP.collidepoint(event.pos):
                    pygame.mixer.music.stop()

        # teclas mantenidas (para ajustar más rápido)
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP]:
            angulo = min(angulo + 1, 89)
        if teclas[pygame.K_DOWN]:
            angulo = max(angulo - 1, 1)
        if teclas[pygame.K_RIGHT]:
            velocidad = min(velocidad + 1, 150)
        if teclas[pygame.K_LEFT]:
            velocidad = max(velocidad - 1, 10)

        # ----- lógica -----
        if bala is not None:
            actualizar_proyectil(bala, dt)

            if hay_colision(bala, objetivo):
                puntos += 1
                mensaje = "¡Le diste! Nuevo objetivo..."
                tiempo_mensaje = 90
                objetivo = nuevo_objetivo()
                bala = None
            elif fuera_de_pantalla(bala):
                mensaje = "Fallaste, ajusta y vuelve a intentar"
                tiempo_mensaje = 90
                bala = None

        if tiempo_mensaje > 0:
            tiempo_mensaje -= 1
            if tiempo_mensaje == 0:
                mensaje = ""

        # ----- dibujo -----
        dibujar_escena(screen, fuente, fondo, angulo, velocidad,
                       objetivo, bala, puntos, disparos, mensaje)
        pygame.display.flip()

    pygame.mixer.music.stop()   # NUEVO
    pygame.quit()


if __name__ == "__main__":
    main()
