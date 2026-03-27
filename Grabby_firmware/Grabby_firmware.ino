// --- PIN CONFIGURATION ---
const int POT_PINS[] = {33, 32, 35, 34, 25}; 
const int BAUD_RATE = 115200;
const int READ_DELAY = 15; 

// --- 🛠️ TUNING PARAMETERS ---
// 1. SMOOTHING_FACTOR (0.05 se 0.2)
const float SMOOTHING_FACTOR = 0.12; 

// 2. DEADBAND (15 se 30): 
const int DEADBAND = 22;           
// ----------------------------

float smooth_vals[5] = {0};
int last_sent[5] = {0};

void setup() {
  Serial.begin(BAUD_RATE);
  
  for(int i=0; i<5; i++) {
    pinMode(POT_PINS[i], INPUT);

    int init_raw = analogRead(POT_PINS[i]);
    smooth_vals[i] = init_raw;
    last_sent[i] = init_raw;
  }
  
  Serial.println("ESP32 Spike-Proof Node Ready");
}

int getMedianSample(int pin) {
  int samples[3];
  samples[0] = analogRead(pin);
  delayMicroseconds(150); 
  samples[1] = analogRead(pin);
  delayMicroseconds(150);
  samples[2] = analogRead(pin);

  // Sorting logic to find Median (middle value)
  if ((samples[0] <= samples[1] && samples[1] <= samples[2]) || (samples[2] <= samples[1] && samples[1] <= samples[0])) return samples[1];
  if ((samples[1] <= samples[0] && samples[0] <= samples[2]) || (samples[2] <= samples[0] && samples[0] <= samples[1])) return samples[0];
  return samples[2];
}

void loop() {
  for (int i = 0; i < 5; i++) {
    // Step 1: Get clean sample (Discard outliers)
    int raw_median = getMedianSample(POT_PINS[i]);

    // Step 2: Apply Exponential Moving Average (EMA)
    smooth_vals[i] = (SMOOTHING_FACTOR * raw_median) + ((1.0 - SMOOTHING_FACTOR) * smooth_vals[i]);

    // Step 3: Apply Deadband (Lock position if change is tiny)
    if (abs((int)smooth_vals[i] - last_sent[i]) > DEADBAND) {
      last_sent[i] = (int)smooth_vals[i];
    }
  }

  // Step 4: Serial Output in your ROS 2 Format (val1,val2,val3,val4,val5.)
  for (int i = 0; i < 5; i++) {
    Serial.print(last_sent[i]);
    if (i < 4) Serial.print(",");
  }
  Serial.println("."); 

  delay(READ_DELAY);
}
