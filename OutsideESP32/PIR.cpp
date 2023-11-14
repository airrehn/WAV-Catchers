#include "PIR.h"

int pir_state = LOW;

void IRAM_ATTR on_pir_motion_detected()
{
  if (millis() - movedtime >  10000){   // if moved, delay of 10s 
    movedtime = millis();
    String msg_moved
    mqttClient.publish(pirmotion, msg_moved, 0, false);
  }
  
}

void init_pir()
{
  pinMode(PIR_INPUT_PIN, INPUT_PULLUP);
  attachInterrupt(PIR_INPUT_PIN, on_pir_motion_detected, RISING);
}

bool is_motion_detected()
{
  int val = digitalRead(PIR_INPUT_PIN);
  if (val == HIGH) {
    if (pir_state == LOW) 
    {
      pir_state = HIGH;
      return true;
    }
  } else {
    if (pir_state == HIGH) 
    {
      pir_state = LOW;
      return false;
    }
  }
  
  return false;
}