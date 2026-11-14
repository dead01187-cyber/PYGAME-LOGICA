# Example file showing a basic pygame "game loop"
import pygame
import sys

# pygame setup
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("Media/musica.mp3")   # NUEVO

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

# NUEVO: botones y fuente
fuente = pygame.font.Font(None, 50)
boton_play = pygame.Rect(390, 310, 220, 100)
boton_stop = pygame.Rect(670, 310, 220, 100)

# NUEVO: cargar las imágenes de fondo en una lista
archivos = [
    "Media/img1_synthwave.png",
    "Media/img2_galaxia.png",
    "Media/img3_aurora.png",
    "Media/img4_tunel.png",
]
imagenes = []
for archivo in archivos:
    img = pygame.image.load(archivo).convert()
    img = pygame.transform.scale(img, (1280, 720))  # que encaje en la ventana
    imagenes.append(img)

# NUEVO: temporizador para cambiar de imagen
indice = 0                 # qué imagen se está mostrando
TIEMPO_CAMBIO = 3000       # 3000 ms = 3 segundos
ultimo_cambio = pygame.time.get_ticks()

# NUEVO: la música empieza sola al abrir
pygame.mixer.music.play(-1)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # NUEVO: clic en los botones
        if event.type == pygame.MOUSEBUTTONDOWN:
            if boton_play.collidepoint(event.pos):
                pygame.mixer.music.play(-1)
            if boton_stop.collidepoint(event.pos):
                pygame.mixer.music.stop()

    # NUEVO: si ya pasaron 3 segundos, pasar a la siguiente imagen
    ahora = pygame.time.get_ticks()
    if ahora - ultimo_cambio >= TIEMPO_CAMBIO:
        indice = (indice + 1) % len(imagenes)  # después de la última regresa a la primera
        ultimo_cambio = ahora

    # NUEVO: en vez de pintar negro, se dibuja la imagen actual de fondo
    screen.blit(imagenes[indice], (0, 0))

    # RENDER YOUR GAME HERE
    # NUEVO: dibujar botones con su texto
    pygame.draw.rect(screen, "green", boton_play)
    pygame.draw.rect(screen, "red", boton_stop)
    texto_play = fuente.render("Reproducir", True, "black")
    texto_stop = fuente.render("Detener", True, "black")
    screen.blit(texto_play, texto_play.get_rect(center=boton_play.center))
    screen.blit(texto_stop, texto_stop.get_rect(center=boton_stop.center))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
