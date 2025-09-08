FROM cirrusci/flutter:3.22.2
WORKDIR /app
COPY . .
RUN flutter pub get
EXPOSE 5173
CMD ["bash", "-lc", "flutter run -d web-server --web-port 5173 --web-hostname 0.0.0.0"]
