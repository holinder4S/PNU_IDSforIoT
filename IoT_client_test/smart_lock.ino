#include <Bridge.h>
#include <YunServer.h>
#include <YunClient.h>

int LEDPIN = 13; // LED PIN 번호
bool DoorLocked = true; //잠겨있을 경우 true
int DoorLockingCount = 0; //잠기기까지 시간을 카운트
YunServer server;
const int TriggerPin = 7; //초음파센서 Trig pin
const int EchoPin = 6; //초음파센서 Echo pin
const int CloseDistance = 500;
long Duration = 0;
long Distance_mm = 0;

void setup() {
  // 1. 와이파이와 연결
  
  // Start our connection
  pinMode(TriggerPin, OUTPUT); // Trigger is an output pin
  pinMode(EchoPin, INPUT); // Echo is an input pin
  Serial.begin(9600); // Serial Output  pinMode(TriggerPin, OUTPUT); // Trigger is an output pin
  pinMode(EchoPin, INPUT); // Echo is an input pin
  Serial.begin(9600); // Serial Output
  Serial.begin(9600);
  pinMode(LEDPIN,OUTPUT);
  digitalWrite(LEDPIN,HIGH); // turn on Led while connecting
  Bridge.begin();  

  // Show a fancy flash pattern once connected
  digitalWrite(LEDPIN,LOW); 
  delay(150);
  digitalWrite(LEDPIN,HIGH); 
  delay(150);
  digitalWrite(LEDPIN,LOW); 
  delay(150);
  digitalWrite(LEDPIN,HIGH); 
  delay(150);
  digitalWrite(LEDPIN,LOW); 
  delay(150);
  
  // Disable for some connections:
  // Start listening for connections  
  
  // server.listenOnLocalhost();
  server.begin();
 
}

void loop() {
  //상태를 확인하고 문 상태를 변경하는 곳
  if(DoorLocked) {
    digitalWrite(LEDPIN, HIGH);
  } else {
    digitalWrite(LEDPIN, LOW);
  }
  // Listen for clients
   
  YunClient client = server.accept();
  // Client exists?
  Serial.print(client);
  if (client) {
    // Lets process the request!
    process(client);
    client.stop();
  }
  /*
   * 문이 닫혀있는 상태일 때 & 문이 잠겨있지 않은 상태일 때 => 5초간 카운팅 한 후 자동으로 잠겨짐 
   */
  AutoLock();
}

void process(YunClient client) {
  
   // Collect user commands
  
  pinMode(13,OUTPUT);
  String command = client.readStringUntil('\\'); // load whole string
  // Enable HTML
  client.println("Status: 200");
  client.println("Content-type: text/html");
  client.println();
  
  // Show UI
  client.println("<B><Center>");
  client.println("<a href='http://ids.local/arduino/abkt11241\\'>Lock</a><br>");
  client.println("<a href='http://ids.local/arduino/ktnl34424\\'>unlock</a><br>");
  client.print("Command:");
  client.println(command);
  if(DoorCloseStat()) {
    client.println("State : Door Close");
  } else {
    client.println("State : Door Open");
  }
  client.println(command.equals("on"));
  client.println("</B></Center>");
  Serial.print("thispoint");
  
  // Turn on
  if (command.indexOf("abkt11241") != -1) {
    DoorLocked = true;
    client.println(command.indexOf("abkt11241"));
  }
  if (command.indexOf("ktnl34424") != -1) {
    DoorLocked = false;
    client.println(command.indexOf("ktnl34424"));
  }
  DoorLockingCount = 0;
}

void AutoLock() {
  // 1. 문이 잠겨있는 상태인 경우 => 아무동작을 하지 않는다
  if(DoorLocked) {
    ;
  }
  // 2. 문이 잠겨있지 않은 상태인 경우
  else {
    
    // 2-1. 문이 닫혀있는 상태인 경우(초음파 센서 거리가 일정거리 이하인 경우 => 카운팅을 한다.
    if(DoorCloseStat()) {
      if(DoorLockingCount > 300) {
        DoorLocked = true;
      } else {
        DoorLockingCount++;
      }
    }
    // 2-2. 문이 열려있는 상태인 경우(초음파 센서 거리가 일정거리 이상인 경우 => 카운팅을 초기화한다
    else {
      DoorLockingCount = 0;
    }
  }
}

bool DoorCloseStat() {
    
  digitalWrite(TriggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(TriggerPin, HIGH); // Trigger pin to HIGH
  delayMicroseconds(10); // 10us high
  digitalWrite(TriggerPin, LOW); // Trigger pin to HIGH

  Duration = pulseIn(EchoPin, HIGH); // Waits for the echo pin to get high
  // returns the Duration in microseconds

  Distance_mm = Distance(Duration); // Use function to calculate the distance

  if(Distance_mm < CloseDistance) {
    return true;
  } else {
    return false;
  }
}

long Distance(long time) {
  // Calculates the Distance in mm
  // ((time)*(Speed of sound))/ toward and backward of object) * 10

  long DistanceCalc; // Calculation variable
  DistanceCalc = ((time / 2.9) / 2); // Actual calculation in mm
  //DistanceCalc = time / 74 / 2; // Actual calculation in inches
  return DistanceCalc; // return calculated value
}
