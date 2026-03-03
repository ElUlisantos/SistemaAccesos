//librerías necesarias
#include <SPI.h>
#include <pitches.h>
#include <MFRC522.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

//pines de conexión RFID
#define SCK_PIN  18
#define MISO_PIN 19
#define MOSI_PIN 23
#define SS_PIN   5
#define RST_PIN  21

//pines de leds
#define LED_AZUL 12
#define LED_ROJO 13
#define LED_VERDE 14

//pin para el buzzer
#define BUZZ 22

//pin para el servo
#define SERVO 25

//Creación de objetos
Servo myservo;

MFRC522 rfid(SS_PIN, RST_PIN);

//para la conexión wifi ()
const char* ssid = "TP-Link_BC26";
const char* password = "60706720";

// La IP de la computadora donde corre Django y la ruta de tu vista
// IMPORTANTE: Cambia "192.168.1.100" por la IP local real de tu PC
const char* serverName = "http://192.168.0.105:8000/api/verificar/";
//funciones para el manejo del acceso
void usuarioRechazado(){
  //prender el led rojo y el buzzer
  digitalWrite(LED_ROJO,HIGH);
  tone(BUZZ,NOTE_DS3,250);
  delay(500);
  tone(BUZZ,NOTE_DS3,250);
  delay(500);
  //delay(1000);
  digitalWrite(LED_ROJO,LOW);
}

void usuarioAceptado(){
  //prender el led rojo y el buzzer
  digitalWrite(LED_VERDE,HIGH);
  tone(BUZZ,NOTE_DS3,250);
  delay(1000);
  digitalWrite(LED_VERDE,LOW);
  myservo.write(180); //se puede cambiar el movimiento
  delay(2000);
  myservo.write(0);
}

//verificar el acceso en el servidor
void verificarAccesoServidor(String uid) {
  // Verificar que seguimos conectados al Wi-Fi
  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Iniciar la conexión con la URL del servidor Django
    http.begin(serverName);
    
    // Especificar que enviaremos datos en formato JSON
    http.addHeader("Content-Type", "application/json");
    
    // Armar el JSON manualmente (coincide con json.loads(request.body) en Django)
    String jsonPayload = "{\"id_Tarjeta\":\"" + uid + "\"}";
    
    // Enviar la petición POST
    int httpResponseCode = http.POST(jsonPayload);
    
    // Procesar la respuesta
    if (httpResponseCode > 0) {
      Serial.print("Código de respuesta HTTP: ");
      Serial.println(httpResponseCode);
      
      // Obtener el JSON de respuesta de Django
      String payload_respuesta = http.getString();

      //objeto para parsear el JSON
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, payload_respuesta);

      Serial.println("Respuesta del servidor:");
      Serial.println(payload_respuesta);

      //extracción de los datos del JSON
      bool acceso = doc["acceso"]; 
      const char* mensaje = doc["mensaje"];

      Serial.print("Resultado: ");
      Serial.println(mensaje);

      //lógica de los accesos
      if(acceso){
        usuarioAceptado();
      }else{
        usuarioRechazado();
      }
    } 
    else {
      Serial.print("Error en la petición HTTP. Código de error: ");
      Serial.println(httpResponseCode);
      // Imprimir el mensaje de error exacto
      Serial.println(http.errorToString(httpResponseCode).c_str());
      //poner el código de error con algo
      Serial.println("Revise la conexión con el servidor");
    }
    
    // Liberar recursos
    http.end();
  } else {
    Serial.println("Error: Desconectado del Wi-Fi");
  }
}

void conexionWiFi(){
  WiFi.begin(ssid, password);
  Serial.print("Conectando al Wi-Fi");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a la red Wi-Fi");
  Serial.print("Dirección IP de la ESP32: ");
  Serial.println(WiFi.localIP());
}



void setup() {
  Serial.begin(115200);
  // Inicializacion del RFID
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN); 
  rfid.PCD_Init();
  //
  rfid.PCD_SetAntennaGain(rfid.RxGain_max);
  // Verificación visual de versión del Firmware
  byte v = rfid.PCD_ReadRegister(rfid.VersionReg);
  Serial.print(F("Versión del Firmware MFRC522: 0x"));
  Serial.println(v, HEX);
  if (v == 0x00 || v == 0xFF) {
    Serial.println(F("ERROR: No se detecta el módulo. Revisa conexiones."));
  } else {
    Serial.println(F("Módulo MFRC522 detectado correctamente."));
  }
  //inicialización de pines generales:
  pinMode(LED_AZUL, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);
  pinMode(BUZZ, OUTPUT);
  digitalWrite(LED_AZUL, HIGH);
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_ROJO, LOW);
  //para el servo
  ESP32PWM::allocateTimer(0);
  myservo.setPeriodHertz(50);
  myservo.attach(SERVO, 500, 2400);
  myservo.write(0);
  //
  conexionWiFi();
}


void loop() {
  delay(10);
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }
  //variable para guardar el ID leido
  String uid_leido = ""; 

  Serial.print("UID Detectado: ");

  for (byte i = 0; i < rfid.uid.size; i++) {
      // 2. Formateamos cada byte a Hexadecimal (ej: 0A, 1F)
      if (rfid.uid.uidByte[i] < 0x10) {
          uid_leido += "0"; // Añade un cero inicial si el valor es menor a 16
      }
      uid_leido += String(rfid.uid.uidByte[i], HEX);
  }

  //Convertir a mayusculas para la BD ()
  uid_leido.toUpperCase(); 

  Serial.println(uid_leido); // Verificamos en el monitor serial

  //enviar la solicitud al servidor
  verificarAccesoServidor(uid_leido);
  
  //salida segura en la comunicación con el sensor 
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  

  delay(1000);
}
