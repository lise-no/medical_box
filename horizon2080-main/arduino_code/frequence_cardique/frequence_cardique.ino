// ===============================
// XD-58C + Arduino Uno
// Lecture du rythme cardiaque
// Envoi des données au PC par USB
// ===============================

const int sensorPin = A0;

// Variables BPM
int sensorValue = 0;
int threshold = 550;       // À ajuster selon ton capteur
bool beatDetected = false;

unsigned long lastBeatTime = 0;
unsigned long currentTime = 0;

int BPM = 0;

// Pour éviter de détecter plusieurs fois le même battement
const unsigned long minBeatInterval = 300; // 300 ms = max 200 BPM

void setup() {
  Serial.begin(115200);

  Serial.println("XD-58C - Demarrage");
  Serial.println("Place ton doigt sur le capteur...");
}

void loop() {

  // Lecture du signal analogique
  sensorValue = analogRead(sensorPin);

  currentTime = millis();

  // Détection d'un battement
  if (sensorValue > threshold && !beatDetected) {

    // Vérifie qu'il s'est écoulé suffisamment de temps
    if (currentTime - lastBeatTime > minBeatInterval) {

      // Si ce n'est pas le premier battement
      if (lastBeatTime != 0) {

        unsigned long interval = currentTime - lastBeatTime;

        // Calcul du BPM
        BPM = 60000 / interval;

        // Limitation des valeurs aberrantes
        if (BPM >= 40 && BPM <= 200) {

          Serial.print("Signal: ");
          Serial.print(sensorValue);

          Serial.print(" | BPM: ");
          Serial.println(BPM);
        }
      }

      lastBeatTime = currentTime;
    }

    beatDetected = true;
  }

  // Attend que le signal redescende
  if (sensorValue < threshold) {
    beatDetected = false;
  }

  delay(5);
}
