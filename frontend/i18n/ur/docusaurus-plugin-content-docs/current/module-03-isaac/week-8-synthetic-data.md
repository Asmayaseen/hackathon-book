# ہفتہ 8: مصنوعی ڈیٹا جنریشن

## مصنوعی ڈیٹا کا انقلاب

تربیتی ڈیٹا کو دستی طور پر لیبل کرنا مہنگا اور وقت کھانے والا ہے۔ اشیاء کی شناخت کے لئے ایک اینوٹیٹڈ امیج کی لاگت $0.50-$5.00 ہو سکتی ہے۔ 100,000 امیجز کے ڈیٹا سیٹ کے لئے، اس کا مطلب 50,000-$500,000 لیبلنگ کی لاگت میں ہے۔

**مصنوعی ڈیٹا جنریشن** اس کو حل کرتا ہے سیمولیشن میں خود بخود لیبل شدہ تربیتی ڈیٹا تخلیق کر کے۔ Isaac Sim فی گھنٹہ ہزاروں مکمل طور پر لیبل شدہ امیجز تخلیق کر سکتا ہے نیار-صفر حاشیہ لاگت پر۔

## ڈومین رینڈمائزیشن

کامیاب سیم-ٹو-ریل ٹرانسفر کی کلید **ڈومین رینڈمائزیشن** ہے - منظر کے پیرامیٹرز کو منظم طریقے سے متغیر کرنا تاکہ حقیقی دنیا کی تغیرات کو کور کرنے والی تنوع پیدا کیا جا سکے۔

### رینڈمائزیشن پیرامیٹرز

1. **لائٹنگ**: شدت، رنگ کا درجہ حرارت، زاویہ
2. **ٹیکسچرز**: سطح کے مواد، رنگ، ریفلیکٹویٹی
3. **اوبجیکٹ کی پوزیشن**: پوزیشن، گردش، اسکیل
4. **کیمرہ پیرامیٹرز**: FOV، ایکسپوزر، فوکس
5. **پس منظر**: بے ترتیب، محرکات، ماحول

## Isaac Sim Replicator کا استعمال

Replicator Isaac Sim کا مصنوعی ڈیٹا جنریشن فریم ورک ہے، جو رینڈمائزڈ ڈیٹا سیٹس تخلیق کرنے کے لئے ہائی-لیول APIs فراہم کرتا ہے۔

### بنیادی مصنوعی ڈیٹا سیٹ جنریشن

```python
import omni.replicator.core as rep
from omni.isaac.kit import SimulationApp

# تیز جنریشن کے لئے ہیڈ لیس سیمولیشن شروع کریں
simulation_app = SimulationApp({"headless": True})

# امیجز کیفتنے کے لئے کیمرہ کی وضاحت کریں
camera = rep.create.camera(
    position=(2.0, 2.0, 1.5),  # کیمرہ کا مقام
    look_at=(0, 0, 0)           # کیمرہ کو اصل پر نکالیں
)

# رینڈمائزڈ سین تخلیق کریں
def create_scene():
    # ہدف کی اشیاء کی نمائندگی کرنے والا بے ترتیب کیوب
    cube = rep.create.cube(
        position=rep.distribution.uniform((-1, -1, 0.5), (1, 1, 1.5)),
        scale=rep.distribution.uniform(0.2, 0.5),
        semantics=[("class", "target_object")]  # شناخت کے لئے لیبل
    )

    # کیوب میٹریل/رنگ رینڈمائز کریں
    with cube:
        rep.randomizer.color(
            colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
        )

    # بے ترتیب لائٹنگ سمت اور شدت
    light = rep.create.light(
        light_type="Distant",  # ہدف والی لائٹ (سورج جیسا)
        intensity=rep.distribution.uniform(500, 3000),
        rotation=rep.distribution.uniform((0, -180, 0), (0, 180, 0))
    )

    return cube, light

# رینڈمائزیشن گراف رجسٹر کریں
rep.randomizer.register(create_scene)

# مختلف اینوٹیشن اقسام کے لئے آؤٹ پٹ رائٹرز کنفیگر کریں
# 1. RGB امیجز
rgb_writer = rep.WriterRegistry.get("BasicWriter")
rgb_writer.initialize(
    output_dir="./synthetic_data/rgb",
    rgb=True
)

# 2. سیمینٹک سیگمینٹیشن (پکسل-وائز کلاس لیبلز)
semantic_writer = rep.WriterRegistry.get("BasicWriter")
semantic_writer.initialize(
    output_dir="./synthetic_data/semantic",
    semantic_segmentation=True
)

# 3. باؤنڈنگ باکسز اشیاء کی شناخت کے لئے
bbox_writer = rep.WriterRegistry.get("BasicWriter")
bbox_writer.initialize(
    output_dir="./synthetic_data/bbox",
    bounding_box_2d_tight=True
)

# تمام رائٹرز کو کیمرہ سے منسلک کریں
rgb_writer.attach([camera])
semantic_writer.attach([camera])
bbox_writer.attach([camera])

# 1000 رینڈمائزڈ فریم تخلیق کریں
with rep.trigger.on_frame(num_frames=1000):
    rep.randomizer.create_scene()

# جنریشن کو انجام دینے کے لئے آرکیسٹریٹر چلائیں
rep.orchestrator.run()

simulation_app.close()
print("1000 مصنوعی تربیتی نمونے تخلیق کیے گئے")
```

## ادراک گراؤنڈ ٹروتھ

Isaac Sim خود بخود **مکمل لیبلز** مختلف ادراک کاموں کے لئے تخلیق کرتا ہے:

### 1. 2D باؤنڈنگ باکسز

اشیاء کے گرد پکسل-مکمل باکسز اشیاء کی شناخت کی تربیت کے لئے (YOLO، Faster R-CNN)۔

### 2. انسٹینس سیگمینٹیشن

انفرادی اشیاء کی نمائندگی کرنے والے پکسل-وائز ماسکس۔

### 3. ڈیپتھ میپس

کیمرہ سے فی-پکسل فاصلہ اسٹیریو وژن اور 3D تعمیر کے لئے۔

### 4. 6-DOF پوز

ہر اشیاء کے لئے 3D پوزیشن (x, y, z) اور اورینٹیشن (roll, pitch, yaw)۔

```python
# اعلیٰ درجے کی گراؤنڈ ٹروتھ جنریشن
import omni.replicator.core as rep

camera = rep.create.camera()

# متعدد اینوٹیشن اقسام کو ایک ساتھ فعال کریں
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="./multi_annotation",
    rgb=True,                          # RGB امیجز
    bounding_box_2d_tight=True,        # 2D ڈیٹیکشن باکسز
    bounding_box_3d=True,              # 3D اورینٹیڈ باکسز
    semantic_segmentation=True,        # پکسل-وائز کلاس لیبلز
    instance_segmentation=True,        # پکسل-وائز انسٹینس IDs
    distance_to_camera=True,           # ڈیپتھ میپ
    distance_to_image_plane=True,      # پلانر ڈیپتھ
    normals=True,                      # سطح کے نارملز
    motion_vectors=True                # آپٹیکل فلو
)
writer.attach([camera])
```

## ہیومنوائڈ ادراک کے لئے حسب ضرورت ڈیٹا سیٹ تخلیق کرنا

یہ مثال ہیومنوائڈ روبوٹ کے لئے اشیاء کی شناخت کے لئے تربیتی ڈیٹا تخلیق کرتی ہے جنہیں وہ مینوپولیٹ کر سکتا ہے:

```python
import omni.replicator.core as rep

# ہیومنوائڈ کو ڈیٹیکٹ کرنا چاہیے اشیاء کی وضاحت کریں
def create_manipulation_scene():
    # بے ترتیب ٹیکسچر کے ساتھ زمینی طیل
    floor = rep.create.plane(
        scale=10,
        semantics=[("class", "floor")]
    )
    with floor:
        rep.randomizer.texture(
            textures=["./textures/wood.jpg", "./textures/tile.jpg"]
        )

    # ہیومنوائڈ کمر کی اونچائی پر ٹیبل
    table = rep.create.cube(
        position=(1.0, 0, 0.75),
        scale=(1.0, 0.6, 0.05),
        semantics=[("class", "table")]
    )

    # ٹیبل پر رینڈمائزڈ ہدف اشیاء
    obj_types = ["cube", "sphere", "cylinder"]
    for i in range(3):  # 3 بے ترتیب اشیاء
        obj = rep.create.from_usd(
            f"./assets/{rep.distribution.choice(obj_types)}.usd",
            position=rep.distribution.uniform(
                (0.5, -0.3, 0.80),  # ٹیبل سطح کی حدیں
                (1.5, 0.3, 0.80)
            ),
            semantics=[("class", "manipulable_object")]
        )
        with obj:
            # بے ترتیب مواد ماڈل کو ظہور کے لئے مستحکم بناتا ہے
            rep.randomizer.color(
                colors=rep.distribution.uniform((0, 0, 0), (1, 1, 1))
            )

    # ہیومنوائڈ آنکھ کی سطح کا کیمرہ (160cm اونچائی)
    camera = rep.create.camera(
        position=(0, 0, 1.6),
        rotation=rep.distribution.uniform((-10, -30, 0), (10, 30, 0))
    )

    return camera

rep.randomizer.register(create_manipulation_scene)

# مسلسل فارمیٹ کے ساتھ ڈیٹا سیٹ تخلیق کریں
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="./humanoid_manipulation_dataset",
    rgb=True,
    bounding_box_2d_tight=True,
    semantic_segmentation=True
)

camera = create_manipulation_scene()
writer.attach([camera])

# 5000 تربیتی امیجز تخلیق کریں
with rep.trigger.on_frame(num_frames=5000):
    rep.randomizer.create_manipulation_scene()

rep.orchestrator.run()
```

## بہترین مشقیں

1. **حقیقی سینسرز سے مماثل**: کیمرہ ریزولوشن، FOV، اور نوائس کو اس طرح کنفیگر کریں کہ یہ آپ کے جسمانی روبوٹ کے سینسرز سے مماثل ہو۔
2. **کافی تنوع**: دستی طور پر جمع کرنے کے مقابلے میں کم از کم 10x زیادہ مصنوعی ڈیٹا تخلیق کریں۔
3. **ٹرانسفر کی تصدیق**: سیم-ٹو-ریل گیپ کی تصدیق کے لئے تربیت یافتہ ماڈلز کو چھوٹے حقیقی دنیا کے تصدیقی سیٹس پر ٹیسٹ کریں۔
4. **تدریجی پیچیدگی**: سادہ مناظر کے ساتھ شروع کریں، ماڈلز کی بہتری کے ساتھ پیچیدگی شامل کریں۔

## ورزشیں

1. **بنیادی رینڈمائزیشن**: 100 امیجز کا ڈیٹا سیٹ تخلیق کریں بے ترتیب رنگ اور سائز کے ڈبے بے ترتیب پوزیشنز پر۔

2. **لائٹنگ کا مطالعہ**: صرف لائٹنگ رینڈمائز کر کے 50 امیجز ایک ہی سین کے تخلیق کریں۔ دیکھیں کہ یہ اشیاء کی ظہور کو کیسے متاثر کرتا ہے۔

3. **حسب ضرورت اشیاء**: روزمرہ کی اشیاء کا 3D ماڈل درآمد کریں (کپ، بوتل) اور 1000-امیج ڈیٹیکشن ڈیٹا سیٹ تخلیق کریں۔

4. **گراؤنڈ ٹروتھ موازنہ**: RGB + سیمینٹک سیگمینٹیشن جوڑے تخلیق کریں اور RGB امیجز پر اوور لیڈ سیگمینٹیشن ماسکس کو وژوئلائز کریں۔

---

**اگلا**: [ہفتہ 9 - Isaac ROS ڈیپلائمنٹ](./week-9-isaac-ros.md)