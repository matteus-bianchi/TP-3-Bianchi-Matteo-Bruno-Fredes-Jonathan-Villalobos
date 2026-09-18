import asyncio
import os
import shutil
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# CONFIGURACIÓN
# ============================================================

WIDTH = 1080
HEIGHT = 1920
FPS = 30

SEGMENT_DURATION = 6
TOTAL_DURATION = 60

VOICE = "es-AR-ElenaNeural"

OUTPUT = Path("forge_short.mp4")
TEMP = Path("forge_temp")


# ============================================================
# GUION
# ============================================================
#
# 10 partes de 6 segundos = 60 segundos.
#
# El texto de "voice" es lo que dice la voz IA.
# El texto de "subtitle" aparece en pantalla.
#
# ============================================================

SEGMENTS = [

    {
        "voice": (
            "Primero, necesitás Minecraft Java Edition. "
            "Descargá el launcher oficial desde Minecraft punto net "
            "e iniciá sesión con tu cuenta."
        ),
        "subtitle": (
            "1. INSTALÁ MINECRAFT JAVA\n\n"
            "Descargá el launcher oficial\n"
            "desde Minecraft.net"
        )
    },

    {
        "voice": (
            "Abrí el launcher y ejecutá Minecraft Java "
            "una vez con la versión que vas a modificar. "
            "Esto prepara los archivos necesarios."
        ),
        "subtitle": (
            "2. ABRÍ MINECRAFT\n\n"
            "Ejecutá Minecraft Java una vez\n"
            "con la versión que vas a modificar."
        )
    },

    {
        "voice": (
            "Ahora entrá al sitio oficial de Forge "
            "y buscá exactamente la misma versión "
            "de Minecraft que instalaste."
        ),
        "subtitle": (
            "3. DESCARGÁ FORGE\n\n"
            "Entrá a Forge y elegí\n"
            "la misma versión de Minecraft."
        )
    },

    {
        "voice": (
            "En la página de Forge, descargá el Installer. "
            "Elegí siempre la versión que coincida "
            "con tu Minecraft."
        ),
        "subtitle": (
            "4. DESCARGÁ EL INSTALLER\n\n"
            "Elegí el archivo Installer\n"
            "de la versión correcta."
        )
    },

    {
        "voice": (
            "Ejecutá el instalador de Forge, seleccioná "
            "Install Client y presioná OK. "
            "Forge se instalará automáticamente."
        ),
        "subtitle": (
            "5. INSTALÁ FORGE\n\n"
            "Seleccioná \"Install Client\"\n"
            "y presioná OK."
        )
    },

    {
        "voice": (
            "Abrí nuevamente Minecraft Launcher. "
            "En Instalaciones debería aparecer "
            "un nuevo perfil llamado Forge."
        ),
        "subtitle": (
            "6. ABRÍ EL LAUNCHER\n\n"
            "Buscá el nuevo perfil\n"
            "llamado Forge."
        )
    },

    {
        "voice": (
            "Seleccioná Forge y presioná Jugar. "
            "La primera vez puede tardar un poco "
            "mientras prepara todos los archivos."
        ),
        "subtitle": (
            "7. EJECUTÁ FORGE\n\n"
            "Seleccioná Forge → Jugar\n"
            "La primera ejecución puede tardar."
        )
    },

    {
        "voice": (
            "Para instalar mods, cerrá Minecraft. "
            "Presioná Windows más R, escribí porcentaje "
            "appdata porcentaje y abrí la carpeta Minecraft."
        ),
        "subtitle": (
            "8. BUSCÁ LA CARPETA DE MINECRAFT\n\n"
            "Win + R → %appdata%\n"
            "→ .minecraft"
        )
    },

    {
        "voice": (
            "Dentro de Minecraft buscá la carpeta mods. "
            "Si no existe, creala. Después copiá "
            "ahí los archivos JAR de tus mods."
        ),
        "subtitle": (
            "9. AGREGÁ LOS MODS\n\n"
            "Abrí la carpeta \"mods\"\n"
            "y copiá ahí los archivos .JAR."
        )
    },

    {
        "voice": (
            "Por último, asegurate de que los mods sean "
            "compatibles con tu versión de Minecraft y Forge. "
            "Abrí Forge, jugá y listo."
        ),
        "subtitle": (
            "10. ¡LISTO!\n\n"
            "Verificá la compatibilidad de los mods\n"
            "y jugá con Forge."
        )
    }
]


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def run(command, cwd=None):
    """Ejecuta un comando de consola y detiene el programa si falla."""

    print("\n>", " ".join(str(x) for x in command))

    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)

        raise RuntimeError(
            f"El comando falló con código {result.returncode}"
        )

    return result


def check_program(program):
    """Comprueba que FFmpeg esté instalado."""

    if shutil.which(program) is None:
        raise RuntimeError(
            f"No se encontró '{program}'.\n"
            f"Instalá FFmpeg y agregalo al PATH."
        )


def get_font(size, bold=False):

    if bold:
        fonts = [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
    else:
        fonts = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]

    for font in fonts:
        if os.path.exists(font):
            return ImageFont.truetype(font, size)

    return ImageFont.load_default()


# ============================================================
# GENERAR VOZ IA
# ============================================================

async def generate_voice(text, filename):

    print(f"Generando voz: {filename}")

    tts = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="-5%",
        volume="+0%"
    )

    await tts.save(str(filename))


async def generate_all_voices():

    for i, segment in enumerate(SEGMENTS):

        output = TEMP / f"voice_{i:02d}.mp3"

        await generate_voice(
            segment["voice"],
            output
        )


# ============================================================
# OBTENER DURACIÓN DEL AUDIO
# ============================================================

def audio_duration(filename):

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(filename)
        ],
        capture_output=True,
        text=True
    )

    return float(result.stdout.strip())


# ============================================================
# AJUSTAR CADA VOZ A 6 SEGUNDOS
# ============================================================

def fit_audio(input_file, output_file):

    duration = audio_duration(input_file)

    # Si dura más de 6 segundos:
    # aceleramos.
    #
    # Si dura menos:
    # hacemos la voz un poco más lenta.
    #
    # El resultado siempre dura exactamente 6 segundos.

    speed = duration / SEGMENT_DURATION

    filters = []

    while speed > 2:
        filters.append("atempo=2")
        speed /= 2

    while speed < 0.5:
        filters.append("atempo=0.5")
        speed /= 0.5

    filters.append(f"atempo={speed:.6f}")

    filter_string = ",".join(filters)

    run([
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
        "-af",
        f"{filter_string},apad",
        "-t",
        str(SEGMENT_DURATION),
        "-ar",
        "48000",
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(output_file)
    ])


def fit_all_audio():

    for i in range(len(SEGMENTS)):

        source = TEMP / f"voice_{i:02d}.mp3"
        output = TEMP / f"voice_fixed_{i:02d}.wav"

        print(f"Ajustando audio {i + 1}/10...")

        fit_audio(
            source,
            output
        )


# ============================================================
# CREAR FONDOS
# ============================================================

def create_background(index):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (25, 35, 30)
    )

    draw = ImageDraw.Draw(image)

    # Fondo tipo bloques
    block = 90

    for y in range(0, HEIGHT, block):

        for x in range(0, WIDTH, block):

            if ((x // block) + (y // block)) % 2 == 0:
                color = (35, 85, 48)
            else:
                color = (30, 70, 42)

            draw.rectangle(
                [
                    x,
                    y,
                    x + block - 3,
                    y + block - 3
                ],
                fill=color
            )

    # Oscurecer zona central
    overlay = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 0)
    )

    overlay_draw = ImageDraw.Draw(overlay)

    overlay_draw.rounded_rectangle(
        [
            60,
            550,
            WIDTH - 60,
            1370
        ],
        radius=40,
        fill=(0, 0, 0, 185),
        outline=(130, 220, 140, 255),
        width=5
    )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        overlay
    ).convert("RGB")

    draw = ImageDraw.Draw(image)

    # Título
    title_font = get_font(100, bold=True)

    title = "MINECRAFT FORGE"

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=title_font
    )

    title_width = bbox[2] - bbox[0]

    draw.text(
        (
            (WIDTH - title_width) // 2,
            150
        ),
        title,
        font=title_font,
        fill=(255, 255, 255),
        stroke_width=5,
        stroke_fill=(0, 0, 0)
    )

    # Número de paso
    step_font = get_font(55, bold=True)

    step = f"PASO {index + 1} / 10"

    bbox = draw.textbbox(
        (0, 0),
        step,
        font=step_font
    )

    step_width = bbox[2] - bbox[0]

    draw.text(
        (
            (WIDTH - step_width) // 2,
            350
        ),
        step,
        font=step_font,
        fill=(150, 240, 160),
        stroke_width=3,
        stroke_fill=(0, 0, 0)
    )

    output = TEMP / f"background_{index:02d}.png"

    image.save(output)

    return output


def create_all_backgrounds():

    backgrounds = []

    for i in range(len(SEGMENTS)):

        print(f"Creando fondo {i + 1}/10...")

        backgrounds.append(
            create_background(i)
        )

    return backgrounds


# ============================================================
# SUBTÍTULOS
# ============================================================

def ass_time(seconds):

    hours = int(seconds // 3600)

    minutes = int(
        (seconds % 3600) // 60
    )

    seconds = seconds % 60

    return (
        f"{hours}:"
        f"{minutes:02d}:"
        f"{seconds:05.2f}"
    )


def create_subtitles():

    subtitle_file = TEMP / "subtitles.ass"

    with open(
        subtitle_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            "PlayResX: 1080\n"
            "PlayResY: 1920\n"
            "ScaledBorderAndShadow: yes\n"
            "\n"

            "[V4+ Styles]\n"

            "Format: Name, Fontname, Fontsize, "
            "PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, "
            "Spacing, Angle, BorderStyle, Outline, "
            "Shadow, Alignment, MarginL, MarginR, "
            "MarginV, Encoding\n"

            "Style: Default,Arial,62,"
            "&H00FFFFFF,&H00FFFFFF,"
            "&H00000000,&HAA000000,"
            "1,0,0,0,100,100,0,0,1,5,3,"
            "5,80,80,100,1\n"

            "\n"
            "[Events]\n"

            "Format: Layer, Start, End, Style, "
            "Name, MarginL, MarginR, MarginV, "
            "Effect, Text\n"
        )

        for i, segment in enumerate(SEGMENTS):

            start = i * SEGMENT_DURATION
            end = start + SEGMENT_DURATION

            text = segment["subtitle"]

            # ASS utiliza \N para saltos de línea.
            text = text.replace("\n", r"\N")

            f.write(
                "Dialogue: 0,"
                f"{ass_time(start)},"
                f"{ass_time(end)},"
                "Default,,"
                "0,0,0,,"
                f"{text}\n"
            )

    return subtitle_file


# ============================================================
# CREAR VIDEO SIN AUDIO
# ============================================================

def create_video_backgrounds(backgrounds):

    concat = TEMP / "backgrounds.txt"

    with open(
        concat,
        "w",
        encoding="utf-8"
    ) as f:

        for background in backgrounds:

            path = background.resolve().as_posix()

            f.write(
                f"file '{path}'\n"
            )

            f.write(
                f"duration {SEGMENT_DURATION}\n"
            )

        # FFmpeg necesita repetir el último frame.
        last = backgrounds[-1].resolve().as_posix()

        f.write(
            f"file '{last}'\n"
        )

    output = TEMP / "video.mp4"

    run([
        "ffmpeg",
        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        str(concat),

        "-vf",
        f"scale={WIDTH}:{HEIGHT},"
        "format=yuv420p",

        "-r",
        str(FPS),

        "-t",
        str(TOTAL_DURATION),

        "-an",

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "20",

        str(output)
    ])

    return output


# ============================================================
# UNIR TODAS LAS VOCES
# ============================================================

def create_audio():

    concat = TEMP / "audio.txt"

    with open(
        concat,
        "w",
        encoding="utf-8"
    ) as f:

        for i in range(len(SEGMENTS)):

            audio = (
                TEMP /
                f"voice_fixed_{i:02d}.wav"
            )

            path = audio.resolve().as_posix()

            f.write(
                f"file '{path}'\n"
            )

    output = TEMP / "audio.wav"

    run([
        "ffmpeg",
        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        str(concat),

        "-c",
        "copy",

        str(output)
    ])

    return output


# ============================================================
# RENDER FINAL
# ============================================================

def render_final(video, audio, subtitles):

    print("\nRenderizando video final...")

    # FFmpeg trabaja desde TEMP para que el archivo ASS
    # pueda encontrarse correctamente.

    old_directory = os.getcwd()

    try:

        os.chdir(TEMP)

        run([
            "ffmpeg",
            "-y",

            "-i",
            video.name,

            "-i",
            audio.name,

            "-vf",
            f"subtitles={subtitles.name}",

            "-map",
            "0:v:0",

            "-map",
            "1:a:0",

            "-c:v",
            "libx264",

            "-preset",
            "medium",

            "-crf",
            "20",

            "-c:a",
            "aac",

            "-b:a",
            "192k",

            "-pix_fmt",
            "yuv420p",

            "-t",
            str(TOTAL_DURATION),

            "-movflags",
            "+faststart",

            str(
                Path("../") / OUTPUT
            )
        ])

    finally:

        os.chdir(old_directory)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

async def main():

    print("=" * 60)
    print("      FORGE — MINECRAFT MODS SHORT")
    print("=" * 60)

    check_program("ffmpeg")
    check_program("ffprobe")

    # Limpiar archivos anteriores
    if TEMP.exists():
        shutil.rmtree(TEMP)

    TEMP.mkdir()

    print("\n[1/6] Generando voces IA...")
    await generate_all_voices()

    print("\n[2/6] Ajustando voces a 6 segundos...")
    fit_all_audio()

    print("\n[3/6] Creando fondos...")
    backgrounds = create_all_backgrounds()

    print("\n[4/6] Creando subtítulos...")
    subtitles = create_subtitles()

    print("\n[5/6] Creando video...")
    video = create_video_backgrounds(
        backgrounds
    )

    audio = create_audio()

    print("\n[6/6] Uniendo todo...")
    render_final(
        video,
        audio,
        subtitles
    )

    print("\n")
    print("=" * 60)
    print("              ¡VIDEO TERMINADO!")
    print("=" * 60)
    print()
    print(f"Archivo: {OUTPUT.resolve()}")
    print("Duración: 60 segundos")
    print("Resolución: 1080 x 1920")
    print("Formato: MP4")
    print("Voz: IA — Español Argentina")
    print("Subtítulos: centrados y sincronizados")
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())