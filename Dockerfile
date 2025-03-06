# Verwende das offizielle Python-Image mit einer spezifischen Version
#
# !!!!    Achtung Script funktioniert NICHT mit Version 3.13     !!!!
#
FROM python:3.11-slim

# Autoreninformationen
LABEL org.opencontainers.image.authors="Elias Oltmanns <elias.oltmanns@gwdg.de>, Andreas Kasper <andreas.kasper@hdf.de>"

# Installiere Systemabhängigkeiten (z.B. für git) und setze das Arbeitsverzeichnis
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Erstelle ein App-Verzeichnis und klone das Repository
WORKDIR /app
RUN git clone https://github.com/AV-EFI/efi-conv.git

# Installiere die Python-Abhängigkeiten im Entwicklermodus
WORKDIR /app/efi-conv
RUN pip install --no-cache-dir -e .

# Definiere den Standard-Arbeitsordner
WORKDIR /app

# Setze das Standard-Einstiegspunktprogramm
ENTRYPOINT [ "efi-conv" ]