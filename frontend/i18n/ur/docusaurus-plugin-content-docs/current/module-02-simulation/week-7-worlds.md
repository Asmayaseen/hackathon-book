# ہفتہ 7: حسب ضرورت سیمولیشن دنیا تخلیق کرنا

## کیوں حسب ضرورت ماحول اہم ہے

جنرک فلیٹ-گراؤنڈ سیمولیشن اصل دنیا کی چیلنجز کو ظاہر نہیں کر پاتے:

- **زمینی تنوع**: ڈھلوان، سیڑھیاں، ناہموار سطحیں توازن کنٹرولرز کو ٹیسٹ کرتی ہیں
- **رکاوٹیں**: تنگ گزر، متحرک اشیاء کالیژن ایوائڈنس کی تصدیق کرتی ہیں
- **لائٹنگ کی حالتیں**: سایے، ریفلیکشنز وژن-بیسڈ پالیسیز کو متاثر کرتی ہیں
- **ڈومین رینڈمائزیشن**: متغیر فزکس/وژوئلز سیم-ٹو-ریل ٹرانسفر کو بہتر بناتے ہیں

**هدف**: ایسے ماحول تخلیق کریں جو آپ کے روبوٹ کو چیلنج کریں اور ڈیپلائمنٹ منظرناموں کو آئینہ دار کریں۔

## Gazebo: پروسیجرل زمینیں تخلیق کرنا

### ہیٹ میپ زمینیں (DEM ڈیٹا)

**ہیٹ میپس** گریسکیل امیجز کا استعمال کرتے ہیں زمینی بلندی کی وضاحت کے لئے (سفید=اونچا، کالا=کم)۔

```xml
<!-- world_with_terrain.sdf -->
<sdf version="1.8">
  <world name="outdoor_terrain">
    <physics type="bullet">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <!-- امیج سے ہیٹ میپ زمین -->
    <model name="terrain">
      <static>true</static>
      <link name="terrain_link">
        <collision name="terrain_collision">
          <geometry>
            <heightmap>
              <uri>file://terrain_heightmap.png</uri> <!-- 512x512 گریسکیل PNG -->
              <size>100 100 10</size> <!-- چوڑائی گہرائی زیادہ سے زیادہ اونچائی (میٹرز) -->
              <pos>0 0 0</pos>
            </heightmap>
          </geometry>
          <surface>
            <friction>
              <ode><mu>0.8</mu></ode> <!-- مٹی/گھاس کا فرکشن -->
            </friction>
          </surface>
        </collision>

        <visual name="terrain_visual">
          <geometry>
            <heightmap>
              <uri>file://terrain_heightmap.png</uri>
              <size>100 100 10</size>
              <texture>
                <diffuse>file://grass_texture.jpg</diffuse>
                <normal>file://grass_normal.jpg</normal> <!-- تفصیل کے لئے نارمل میپ -->
                <size>10</size> <!-- ہر 10م میں ٹیکسچر دہرائیں -->
              </texture>
            </heightmap>
          </geometry>
        </visual>
      </link>
    </model>

    <!-- متحرک لائٹنگ (سورج وقت کے ساتھ چلتا ہے) -->
    <light name="sun" type="directional">
      <pose>0 0 100 0 0 0</pose>
      <diffuse>0.9 0.9 0.7 1</diffuse> <!-- گرم دن کی روشنی -->
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction> <!-- زاویہ دار دن کی روشنی -->
      <cast_shadows>true</cast_shadows> <!-- حقیقی سایے -->
    </light>
  </world>
</sdf>
```

**پائیتھن کے ساتھ ہیٹ میپ جنریٹ کریں**:

```python
import numpy as np
from PIL import Image

def generate_hilly_terrain(width=512, height=512, num_hills=20):
    """
    گاؤسین بLOBs کا استعمال کرتے ہوئے پروسیجرل ٹیلیں تخلیق کریں۔
    آرگس:
        width, height: امیج کے ابعاد
        num_hills: بے ترتیب ٹیلیں
    واپسی:
        PIL امیج (گریسکیل ہیٹ میپ)
    """
    terrain = np.zeros((height, width), dtype=np.float32)

    for _ in range(num_hills):
        # بے ترتیب ٹیل کا مرکز
        cx = np.random.randint(0, width)
        cy = np.random.randint(0, height)

        # بے ترتیب ٹیل کا سائز اور اونچائی
        sigma = np.random.randint(20, 80)  # ٹیل کی چوڑائی
        amplitude = np.random.uniform(0.3, 1.0)  # اونچائی (0-1 اسکیل)

        # گاؤسین ٹیل تخلیق کریں
        y, x = np.ogrid[:height, :width]
        hill = amplitude * np.exp(-((x - cx)**2 + (y - cy)**2) / (2 * sigma**2))
        terrain += hill

    # 0-255 تک نارملائز (PNG گریسکیل رینج)
    terrain = (terrain / terrain.max() * 255).astype(np.uint8)

    # PNG کے بطور محفوظ کریں
    img = Image.fromarray(terrain, mode='L')
    img.save('terrain_heightmap.png')
    print("ہیٹ میپ محفوظ: terrain_heightmap.png")

# زمین تخلیق کریں
generate_hilly_terrain()
```

### رکاوٹیں اور متحرک اشیاء

```xml
<!-- متحرک رکاوٹیں شامل کریں (ڈبے جنہیں دھکیلا جا سکتا ہے) -->
<model name="obstacle_box_1">
  <pose>5 3 0.5 0 0 0</pose>
  <link name="box_link">
    <inertial>
      <mass>20.0</mass> <!-- 20kg ڈبا (روبوٹ کو چیلنج کرنے کے لئے کافی بھاری) -->
      <inertia><ixx>0.67</ixx><iyy>0.67</iyy><izz>0.67</izz></inertia>
    </inertial>
    <collision name="box_collision">
      <geometry>
        <box><size>1.0 1.0 1.0</size></box>
      </geometry>
      <surface>
        <friction><ode><mu>0.5</mu></ode></friction> <!-- زمین پر کارڈ بورڈ -->
      </surface>
    </collision>
    <visual name="box_visual">
      <geometry><box><size>1.0 1.0 1.0</size></box></geometry>
      <material>
        <ambient>0.7 0.5 0.3 1</ambient> <!-- بھورا کارڈ بورڈ رنگ -->
      </material>
    </visual>
  </link>
</model>

<!-- تنگ دروازہ (0.8م چوڑا - ہیومنوائڈ کے لئے تنگ) -->
<model name="doorway">
  <static>true</static>
  <pose>10 0 0 0 0 0</pose>

  <link name="left_wall">
    <pose>0 -2 1 0 0 0</pose>
    <collision name="wall_collision">
      <geometry><box><size>0.2 4 2</size></box></geometry>
    </collision>
    <visual name="wall_visual">
      <geometry><box><size>0.2 4 2</size></box></geometry>
    </visual>
  </link>

  <link name="right_wall">
    <pose>0 2 1 0 0 0</pose>
    <collision name="wall_collision">
      <geometry><box><size>0.2 4 2</size></box></geometry>
    </collision>
    <visual name="wall_visual">
      <geometry><box><size>0.2 4 2</size></box></geometry>
    </visual>
  </link>
</model>
```

## یونٹی: حقیقی ان ڈور/آؤٹ ڈور مناظر

### یونٹی میں زمین تخلیق

1. **Terrain GameObject**: `GameObject → 3D Object → Terrain`
2. **Brushes کے ساتھ سکلپٹ کریں**:
   - **Raise/Lower**: ٹیلیں اور ویلیز تخلیق کریں
   - **Smooth**: تیز کنارے کم کریں (مستحکم فُٹ کانٹیکٹ کے لئے اہم)
   - **Paint Textures**: گھاس، مٹی، گریول (متعدد لیئرز)

**پروگرامیک زمین تخلیق (C#)**:

```csharp
using UnityEngine;

public class ProceduralTerrain : MonoBehaviour
{
    public int resolution = 513; // زمین کی ریزولوشن (پاور آف 2 + 1)
    public float scale = 20f;    // پرلین نوائس اسکیل (بڑا = ہموار ٹیلیں)
    public float heightMultiplier = 10f; // زیادہ سے زیادہ زمین کی اونچائی

    void Start()
    {
        Terrain terrain = GetComponent<Terrain>();
        TerrainData terrainData = terrain.terrainData;

        // زمین کا سائز سیٹ کریں
        terrainData.heightmapResolution = resolution;
        terrainData.size = new Vector3(100, 20, 100); // چوڑائی، اونچائی، گہرائی

        // پرلین نوائس کا استعمال کرتے ہوئے اونچائی اقدار تخلیق کریں
        float[,] heights = new float[resolution, resolution];

        for (int y = 0; y < resolution; y++)
        {
            for (int x = 0; x < resolution; x++)
            {
                // پرلین نوائس کوآرڈینیٹس
                float xCoord = (float)x / resolution * scale;
                float yCoord = (float)y / resolution * scale;

                // نوائس نمونہ (0-1 رینج)
                float height = Mathf.PerlinNoise(xCoord, yCoord);
                heights[y, x] = height; // یونٹی [y, x] اشاریہ استعمال کرتا ہے
            }
        }

        // اونچائیوں کو زمین پر لاگو کریں
        terrainData.SetHeights(0, 0, heights);

        Debug.Log("پروسیجرل زمین تخلیق کی گئی!");
    }
}
```

**اسکرپٹ منسلک کریں**: Terrain GameObject میں شامل کریں، تخلیق کے لئے Play دبائیں۔

### سیڑھیاں اور متعدد سطح کی ساختیں

```csharp
// پروسیجرلی سیڑھیاں تخلیق کریں (لوکوموشن پالیسیز کو ٹیسٹ کرنا)
public class StairGenerator : MonoBehaviour
{
    public int numSteps = 10;
    public float stepWidth = 1.0f;
    public float stepDepth = 0.3f;
    public float stepHeight = 0.15f; // 15cm اُٹھاؤ (معیاری عمارت کوڈ)
    void Start()
    {
        for (int i = 0; i < numSteps; i++)
        {
            // سٹیپ GameObject تخلیق کریں
            GameObject step = GameObject.CreatePrimitive(PrimitiveType.Cube);
            step.transform.parent = transform;

            // سٹیپ کی پوزیشن
            step.transform.position = new Vector3(
                0,
                i * stepHeight,
                i * stepDepth
            );

            // سٹیپ ابعاد کے لئے اسکیل
            step.transform.localScale = new Vector3(stepWidth, stepHeight, stepDepth);

            // فرکشن شامل کریں (لکڑی کی سیڑھیاں)
            var collider = step.GetComponent<BoxCollider>();
            var material = new PhysicMaterial("StairMaterial");
            material.dynamicFriction = 0.6f;
            material.staticFriction = 0.7f;
            collider.material = material;
        }
    }
}
```

### حقیقی سیم-ٹو-ریل کے لئے لائٹنگ

**اہم اصول**: **متغیر لائٹنگ** کے تحت وژن پالیسیز کی تربیت کریں تاکہ سیمولیشن کی حالت پر اوور فٹنگ سے بچا جا سکے۔

```csharp
// بے ترتیب لائٹنگ کنٹرولر (ڈومین رینڈمائزیشن)
public class LightingRandomizer : MonoBehaviour
{
    public Light directionalLight; // مرکزی سورج کی لائٹ تفویض کریں

    void OnEpisodeBegin() // جب RL ایپی سوڈ ری سیٹ ہوتا ہے کال کیا جاتا ہے
    {
        // بے ترتیب سورج کا زاویہ (روزمرہ کے مختلف اوقات کا شبیہہ)
        float randomAngleX = Random.Range(30f, 70f); // صبح سے دوپہر
        float randomAngleY = Random.Range(-30f, 30f); // مشرق/مغرب کی تغیر
        directionalLight.transform.rotation = Quaternion.Euler(randomAngleX, randomAngleY, 0);

        // بے ترتیب لائٹ شدت
        directionalLight.intensity = Random.Range(0.6f, 1.2f);

        // بے ترتیب رنگ کا درجہ حرارت (گرم/ٹھنڈی لائٹنگ)
        float colorTemp = Random.Range(0.8f, 1.0f);
        directionalLight.color = new Color(1f, colorTemp, colorTemp * 0.9f);
    }
}
```

**اضافی رینڈمائزیشن**:
- **Skybox**: سورج کی پوزیشن تبدیل کرنے کے لئے گھمائیں
- **Fog**: فضائی اسکیٹرنگ شامل کریں (آؤٹ ڈور مناظر)
- **Shadows**: معیار ٹوگل کریں (نرم vs سخت سایے)

## ڈومین رینڈمائزیشن کی بہترین مشقیں

**فزکس رینڈمائزیشن** (فی ایپی سوڈ):

```python
# فزکس کو بے ترتیب بنانے کے لئے Gazebo پلگ ان (جھوٹا کوڈ)
import random

class PhysicsRandomizer:
    def on_episode_reset(self):
        # بے ترتیب گریویٹی (±5%)
        gravity = 9.81 * random.uniform(0.95, 1.05)

        # بے ترتیب زمینی فرکشن (0.6 - 1.4)
        friction = random.uniform(0.6, 1.4)

        # بے ترتیب لنک ماسز (±10%)
        for link in robot.links:
            original_mass = link.mass
            link.mass = original_mass * random.uniform(0.9, 1.1)

        # بے ترتیب جوائنٹ ڈیمپنگ (±20%)
        for joint in robot.joints:
            joint.damping *= random.uniform(0.8, 1.2)
```

**وژوئل رینڈمائزیشن**:
- مواد کے رنگ (RGB چینلز ±30%)
- ٹیکسچر اسکیلز (0.5x - 2x)
- اشیاء کے سائز (±15%)
- کیمرہ ایکسپوزر (±20%)

**سینسر رینڈمائزیشن**:
- LiDAR نوائس stddev: 1-5cm
- کیمرہ لیسی: 10-50ms
- IMU بائس ڈریفٹ: ±0.1 m/s²

## حسب ضرورت دنیا کے لئے ٹیسٹنگ چیک لسٹ

پالیسیز کی تربیت سے پہلے، تصدیق کریں:

- [ ] روبوٹ مستحکم پوز میں اسپون ہوتا ہے (ڈھلکن/تیرنا نہیں)
- [ ] کولیژن جیومیٹری وژوئل سے مماثل ہے (غیر مرئی دیواریں نہیں)
- [ ] فرکشن اقدار حقیقی ہیں (روبوٹ بہت زیادہ سلپ نہیں کرتا)
- [ ] لائٹنگ رینڈرنگ آرٹیفیکٹس کا سبب نہیں بنتی (سایہ ایسنا، z-fighting)
- [ ] ڈومین رینڈمائزیشن رینج فزکس کو توڑتی نہیں ہے (مثلاً منفی ماس)
- [ ] سینسرز متوقع شرح پر ڈیٹا وصول کرتے ہیں (ٹاپک فریکوئنسیز چیک کریں)
- [ ] کارکردگی: سیمولیشن ≥0.5x ریل ٹائم رفتار پر چلتا ہے

**ورزش**: ایک Gazebo دنیا تخلیق کریں جس میں:
1. ہیٹ میپ زمین (کم از کم 3 ٹیلیں)
2. سیڑھیاں (8-10 قدم، 15cm اُٹھاؤ)
3. 3 متحرک ڈبے (رکاوٹیں)
4. تنگ گزر (0.9م چوڑا)

ہیومنوائڈ روبوٹ کو اسپون کریں اور دستی طور پر کنٹرول کریں (کی بورڈ ٹیلی آپ) تاکہ ماحول میں نیوی گیٹ کیا جا سکے۔ دستیاب کریں کہ کون سی رکاوٹیں روبوٹ کو گرنے یا پھنسنے کا سبب بنتی ہیں۔

---

**ماڈیول 2 خلاصہ**: آپ نے Gazebo اور یونٹی میں ہیومنوائڈ روبوٹس کی سیمولیشن سیکھی ہے، حقیقی فزکس کنفیگر کی ہے، نوائس کے ساتھ سینسرز کو ماڈل کیا ہے، اور چیلنجنگ ماحول تخلیق کیے ہیں۔ **اگلا ماڈیول**: [Isaac Sim & Gym](../module-03-isaac/intro.md) - GPU-ایکسلریٹڈ سیمولیشن مسیو پیرالل ٹریننگ کے لئے۔