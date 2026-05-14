import cv2
import mediapipe as mp
import random
import time
import numpy as np
from collections import deque

# --- 1. إعدادات الكاميرا والشاشة ---
width, height = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# --- 2. إعدادات MediaPipe للذكاء الاصطناعي ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# --- 3. وظيفة تصغير الصور والتعامل مع المسارات ---
def load_and_resize(path, size=(130, 130)):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is not None:
        return cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    print(f"⚠️ Warning: Could not find image at {path}")
    return None

# تحميل الصور التي حددتها
try:
    f1 = load_and_resize('indir 1.png')
    f2 = load_and_resize('indir (2).png')
    f3 = load_and_resize('indir (3).png')
    f4 = load_and_resize('indir (4).png')
    f5 = load_and_resize('indir (5).png')
    f6 = load_and_resize('indir (6).png')
    img_bomb = load_and_resize('Bomb Emoji.png')
    
    fruit_images = [f for f in [f1, f2, f3, f4, f5, f6] if f is not None]
    if not fruit_images or img_bomb is None:
        print("❌ Error: Missing essential images. Check file names!")
except Exception as e:
    print(f"❌ Error during loading: {e}")

# --- 4. وظيفة الدمج الشفاف (لتجنب أخطاء الأبعاد) ---
def overlay_transparent(background, overlay, x, y):
    bg_h, bg_w = background.shape[:2]
    h, w = overlay.shape[:2]
    if x >= bg_w or y >= bg_h or x + w <= 0 or y + h <= 0: return background
    
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w, bg_w), min(y + h, bg_h)
    ov_x1, ov_y1 = x1 - x, y1 - y
    ov_x2, ov_y2 = ov_x1 + (x2 - x1), ov_y1 + (y2 - y1)
    
    overlay_crop = overlay[ov_y1:ov_y2, ov_x1:ov_x2]
    background_section = background[y1:y2, x1:x2]
    
    if overlay_crop.shape[2] < 4: return background # تأكد أنها PNG شفافة
    
    overlay_image = overlay_crop[..., :3]
    mask = overlay_crop[..., 3:] / 255.0
    
    combined = (1.0 - mask) * background_section + mask * overlay_image
    background[y1:y2, x1:x2] = combined.astype(np.uint8)
    return background

# --- 5. كلاس الفاكهة والقنبلة ---
class GameItem:
    def __init__(self, is_bomb=False):
        self.is_bomb = is_bomb
        self.reset()

    def reset(self):
        self.x = random.randint(100, width - 150)
        self.y = height
        self.speed_y = random.randint(18, 28) # سرعة الانطلاق
        self.speed_x = random.randint(-5, 5)
        self.active = True
        self.img = img_bomb if self.is_bomb else random.choice(fruit_images)
        self.h, self.w = self.img.shape[:2]
        self.radius = 60 # مسافة الاصطدام

    def update(self):
        self.y -= self.speed_y
        self.x += self.speed_x
        self.speed_y -= 1 # الجاذبية
        if self.y > height + 100: self.active = False

    def draw(self, img):
        if self.active:
            overlay_transparent(img, self.img, int(self.x - self.w//2), int(self.y - self.h//2))

# --- 6. متغيرات اللعبة الأساسية ---
active_items = []
finger_points = deque(maxlen=12) # لرسم الخط خلف الإصبع
score = 0
lives = 3
game_over = False
last_spawn_time = time.time()

# --- 7. حلقة اللعب (Game Loop) ---
while True:
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1) # قلب الصورة لتكون مرآة
    
    if not game_over:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        current_finger_pos = None

        # تتبع اليد
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                # رسم نقاط اليد على الشاشة
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
                # إحداثيات طرف السبابة (Landmark 8)
                lm8 = hand_lms.landmark[8]
                ix, iy = int(lm8.x * width), int(lm8.y * height)
                current_finger_pos = (ix, iy)
                finger_points.appendleft(current_finger_pos)

        # رسم خط السكينة الانسيابي
        for i in range(1, len(finger_points)):
            if finger_points[i-1] is None or finger_points[i] is None: continue
            thickness = int(18 * (1 - i / len(finger_points)))
            cv2.line(img, finger_points[i-1], finger_points[i], (255, 255, 255), thickness)

        # ظهور العناصر كل 1.5 ثانية
        if time.time() - last_spawn_time > 1.5:
            is_bomb = random.random() < 0.2 # 20% احتمال ظهور قنبلة
            active_items.append(GameItem(is_bomb))
            last_spawn_time = time.time()

        # معالجة كل الفواكه والقنابل
        for item in active_items[:]:
            item.update()
            item.draw(img)
            
            # التحقق من القطع
            if current_finger_pos:
                dist = ((item.x - current_finger_pos[0])**2 + (item.y - current_finger_pos[1])**2)**0.5
                if dist < item.radius:
                    if item.is_bomb:
                        lives -= 1
                        if lives <= 0: game_over = True
                    else:
                        score += 1
                    active_items.remove(item)
                    continue
            
            if not item.active:
                active_items.remove(item)

        # واجهة المستخدم (UI)
        cv2.putText(img, f'Score: {score}', (50, 80), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 3)
        cv2.putText(img, f'Lives: {lives}', (width - 280, 80), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 3)

    else:
        # شاشة الـ Game Over
        cv2.rectangle(img, (width//4, height//4), (3*width//4, 3*height//4), (0,0,0), -1)
        cv2.putText(img, "GAME OVER", (width//2 - 220, height//2 - 20), cv2.FONT_HERSHEY_DUPLEX, 2.5, (0, 0, 255), 5)
        cv2.putText(img, f"Score: {score}", (width//2 - 100, height//2 + 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(img, "Press 'R' to Restart", (width//2 - 180, height//2 + 130), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Fruit Ninja Computer Engineering Edition", img)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('r') and game_over:
        score, lives, game_over, active_items = 0, 3, False, []

cap.release()
cv2.destroyAllWindows()