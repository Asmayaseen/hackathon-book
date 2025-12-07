# ہفتہ 8: Isaac Sim کی بنیادیں

![Isaac Sim](/img/ai-9.png)

## Isaac Sim کا تعارف

Isaac Sim NVIDIA کا روبوٹکس سیمولیشن پلیٹ فارم ہے جو Omniverse فریم ورک پر تعمیر کیا گیا ہے۔ روایتی سیمولیٹرز کے برعکس، Isaac Sim RTX رے ٹریسنگ کا استعمال کرتے ہوئے **فوٹو ریلسٹک رینڈرنگ** فراہم کرتا ہے، جس سے مصنوعی ڈیٹا جنریشن ہوتا ہے جو حقیقی دنیا کے سینسر آؤٹ پٹس سے قریب سے مماثل ہوتا ہے۔

## انسٹالیشن اور سیٹ اپ

### سسٹم کی ضروریات

- **GPU**: RTX 2060 یا اعلیٰ (8GB+ VRAM تجویز کردہ)
- **OS**: Ubuntu 20.04/22.04 یا Windows 10/11
- **RAM**: 32GB کم از کم پیچیدہ مناظر کے لئے
- **اسٹوریج**: Isaac Sim + اثاثہ لائبریریز کے لئے 50GB

### انسٹالیشن اسٹیپس

```bash
# NVIDIA Omniverse لانچر ڈاؤن لوڈ کریں
wget https://install.launcher.omniverse.nvidia.com/installers/omniverse-launcher-linux.AppImage

# ایکسیکوٹیبل بنائیں اور لانچ کریں
chmod +x omniverse-launcher-linux.AppImage
./omniverse-launcher-linux.AppImage

# Omniverse لانچر سے، انسٹال کریں:
# 1. Nucleus (مقامی اثاثہ سرور)
# 2. Isaac Sim 2023.1.1 یا بعد کا
```

### انسٹالیشن کی تصدیق

```python
# Isaac Sim Python API ٹیسٹ کریں
from omni.isaac.kit import SimulationApp

# مخصوص کنفیگریشن کے ساتھ سیمولیشن شروع کریں
simulation_app = SimulationApp({
    "headless": False,  # سرور/کلاؤڈ ماحول کے لئے True سیٹ کریں
    "width": 1920,      # ویو پورٹ ریزولوشن
    "height": 1080
})

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid

# ایک سادہ فزکس ٹیسٹ تخلیق کریں
world = World()
# ایک ڈبہ شامل کریں جو گریویٹی کی وجہ سے گرے گا
cube = DynamicCuboid(
    prim_path="/World/Cube",
    position=[0, 0, 2.0],  # زمین سے 2 میٹر اوپر
    size=0.5,               # 50cm ڈبہ
    color=[1.0, 0.0, 0.0]  # لال
)
world.reset()

# 120 فریم کے لئے سیمولیشن چلائیں (60 FPS پر 2 سیکنڈ)
for i in range(120):
    world.step(render=True)  # فزکس اسٹیپ + رینڈر
simulation_app.close()
```

## Omniverse بنیاد کو سمجھنا

### یونیورسل سین ڈسکرپشن (USD)

Isaac Sim Pixar کے USD فارمیٹ کو اس کی بنیاد کے طور پر استعمال کرتا ہے۔ USD ایک **سین ڈسکرپشن فریم ورک** ہے جو یہ اجازت دیتا ہے:
- **لیئرڈ کمپوزیشن** - تبدیلیوں کو اسٹیک کر کے غیر تباہ کن ایڈیٹنگ
- **ٹائم-سیمپلڈ ڈیٹا** - اینیمیشنز اور متحرک خصوصیات کو مؤثر طریقے سے ذخیرہ کیا گیا
- **تعاون** - متعدد صارفین ایک وقت میں مختلف پہلوؤں کو ایڈیٹ کر سکتے ہیں

```python
from pxr import Usd, UsdGeom, Gf

# USD اسٹیج تخلیق کریں (3D مواد کے لئے کنٹینر)
stage = Usd.Stage.CreateNew("robot_scene.usd")

# ٹرانسفارم کی وضاحت کریں (3D سپیس میں پوزیشن/گردش)
xform = UsdGeom.Xform.Define(stage, "/World/Robot")
xform.AddTranslateOp().Set(Gf.Vec3d(1.0, 0.0, 0.5))  # پوزیشن (x, y, z)

# روبوٹ باڈی کی نمائندگی کرنے والا کیوب میش شامل کریں
cube = UsdGeom.Cube.Define(stage, "/World/Robot/Body")
cube.GetSizeAttr().Set(0.3)  # 30cm کیوب

# اسٹیج کو ڈسک میں محفوظ کریں
stage.GetRootLayer().Save()
print("USD سین robot_scene.usd میں محفوظ")
```

## فوٹorealism کے لئے RTX رے ٹریسنگ

Isaac Sim NVIDIA RTX GPU کا فائدہ اٹھاتا ہے **پاتھ-ٹریسڈ رینڈرنگ** کے لئے، جس سے روشنی کی فزکس کو سیمولیٹ کیا جاتا ہے تاکہ حقیقی امیجز پیدا ہوں:

### کلیدی رینڈرنگ کی خصوصیات

1. **گلوبل ایلومینیشن** - روشنی سطحوں سے حقیقی طور پر باؤنس ہوتی ہے
2. **ریفلیکشنز اور ریفریکشنز** - دھاتی سطحیں اور گلاس درست طور پر رینڈر ہوتے ہیں
3. **درست سایے** - حقیقی دنیا کی لائٹنگ کنڈیشنز سے مماثل نرم سایے

```python
import omni.replicator.core as rep

# RTX رے ٹریسنگ پیرامیٹرز کنفیگر کریں
rep.settings.set_render_rtx_realtime()  # ریل ٹائم RTX موڈ

# فی پکسل نمونے سیٹ کریں (اعلی = بہتر معیار، سست رینڈر)
rep.settings.set_rtx_subframes(4)  # 4 نمونے/پکسل توازن

# صاف آؤٹ پٹ کے لئے ڈی نوائسنگ فعال کریں
rep.settings.carb_settings("/rtx/post/dlss/execMode", 1)
```

### کیوں فوٹorealism اہم ہے

**سیم-ٹو-ریل ٹرانسفر** کے لئے، مصنوعی تربیتی ڈیٹا کو حقیقی سینسر آؤٹ پٹس سے مماثل ہونا چاہیے۔ RTX رینڈرنگ پیدا کرتا ہے:
- **حقیقی لائٹنگ** گودام/فیکٹری ماحول سے مماثل
- **میٹریل خصوصیات** (دھات، پلاسٹک، فیبرک) جو ادراک کو متاثر کرتی ہیں
- **سینسر نوائس سیمولیشن** کیمرز اور ڈیپتھ سینسرز کے لئے

## اپنی پہلی سیمولیشن تخلیق کریں

### ہیومنوائڈ روبوٹ لوڈ کرنا

```python
from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.nucleus import get_assets_root_path
from omni.isaac.core.utils.stage import add_reference_to_stage

# فزکس کے ساتھ دنیا شروع کریں
world = World(stage_units_in_meters=1.0)

# NVIDIA اثاثہ سرور پاتھ حاصل کریں
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    raise Exception("Isaac Sim اثاثہ فولڈر نہیں مل سکا")

# Carter روبوٹ لوڈ کریں (ٹیسٹ کے لئے وہیلڈ روبوٹ)
robot_usd_path = assets_root_path + "/Isaac/Robots/Carter/carter_v1.usd"
add_reference_to_stage(
    usd_path=robot_usd_path,
    prim_path="/World/Carter"  # منظر کے جڑ میں جہاں رکھنا ہے
)

world.reset()

# انٹرایکٹو سیمولیشن چلائیں (UIT سے باہر نکلنے کے لئے STOP دبائیں)
while simulation_app.is_running():
    world.step(render=True)
simulation_app.close()
```

## ورزشیں

1. **سین کنسٹرکشن**: ایک USD سین تخلیق کریں جس میں ایک زمینی طیل، تین رنگین ڈبے مختلف اونچائیوں پر، اور ایک ہدف والی لائٹ ماخذ ہو۔

2. **فزکس ایکسپلوریشن**: ڈبہ گرنے کی مثال کو تبدیل کریں تاکہ 5 کروں کے ساتھ ایک نیوٹن کریل تخلیق ہو۔ سیمولیشن میں توانائی کی حفاظت دیکھیں۔

3. **RTX موازنہ**: RTX کے ساتھ اور بغیر RTX کے ایک ہی سین کو رینڈر کریں۔ ویژوئل معیار اور رینڈرنگ ٹائم کا موازنہ کریں۔

4. **روبوٹ لوڈنگ**: Isaac اثاثوں سے Franka Emika Panda روبوٹ لوڈ کریں اور اسے (0, 0, 1.0) پر پوزیشن کریں۔

---

**اگلا**: [ہفتہ 8 - مصنوعی ڈیٹا جنریشن](./week-8-synthetic-data.md)