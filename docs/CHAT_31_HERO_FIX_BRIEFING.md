# CHAT 31 CRITICAL BRIEFING — Hero Component Three.js Fix

**Date:** 2026-02-23
**Issue:** Hero Three.js effect not matching approved wireframe
**Status:** RESOLVED - New Hero.tsx provided
**Next Step:** Chat 31 must answer verification questions before continuing

---

## 🚨 WHAT WENT WRONG

You (Chat 31) created a Hero.tsx component that rendered correctly but had **the wrong Three.js shader algorithm**. The effect had a noticeable fade-in delay and didn't match the approved wireframe's instant reveal behavior.

**The problem was NOT:**
- ❌ React/Next.js structure
- ❌ Event handlers
- ❌ Image loading
- ❌ UI/CSS layout

**The problem WAS:**
- ✅ The blob shader used a **different algorithm** than the wireframe
- ✅ The shader decay/buildup logic was fundamentally different
- ✅ The brush calculation method was completely different

---

## 📊 ALGORITHM COMPARISON

### **YOUR IMPLEMENTATION (WRONG)**

**Shader approach:**
- Used FBM (Fractional Brownian Motion) noise for brush edges
- Distance-based brush calculation
- Conditional decay based on `pointerAlpha` state
- Brush strength multiplier (×4.0) to compensate for slow buildup

**Key code (lines 103-158 in your version):**
```glsl
fragmentShader: `
  // ...
  float decay = pointerAlpha > 0.5 ? 0.98 : 0.92;
  float val = fb.r * decay;

  vec2 corrected = vec2(mousePos.x * aspect, mousePos.y);
  vec2 uvCorrected = vec2((uv.x - 0.5) * aspect, uv.y - 0.5);
  float d = length(uvCorrected - corrected);

  float noiseFactor = fbm(uv * 12.0 + time * 0.3);
  float edgeNoise = (noiseFactor - 0.5) * 0.08;
  float effectiveRadius = pointerRadius + edgeNoise;

  if(d < effectiveRadius){
    float brush = smoothstep(effectiveRadius, effectiveRadius * 0.6, d);
    val = max(val, brush * pointerAlpha * 4.0);
  }
  
  val = clamp(val, 0.0, 1.0);
  gl_FragColor = vec4(val, val, val, 1.0);
`
```

**Why this caused the delay:**
1. `decay` only changes based on `pointerAlpha` state
2. Brush adds `0.25 × brushValue × 4.0 × pointerAlpha` per frame
3. With `decay = 0.98`, it takes ~10 frames to reach full brightness
4. Result: 166ms visible fade-in (at 60fps)

---

### **WIREFRAME IMPLEMENTATION (CORRECT)**

**Shader approach:**
- Angle-based noise for organic brush shape
- Dual noise layers (`nv` and `nv2`) for more complexity
- Time-based decay (not state-based)
- Natural buildup without multipliers

**Key code (from approved wireframe):**
```glsl
fragmentShader: `
  uniform float dTime, aspect, pointerDown, pointerRadius, pointerDuration, time;
  uniform vec2 pointer;
  uniform sampler2D fbTexture;
  varying vec2 vUv;

  float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123); }
  float noise(vec2 p){
    vec2 i=floor(p); vec2 f=fract(p); f=f*f*(3.0-2.0*f);
    float a=hash(i); float b=hash(i+vec2(1.,0.)); 
    float c=hash(i+vec2(0.,1.)); float d=hash(i+vec2(1.,1.));
    return mix(mix(a,b,f.x),mix(c,d,f.x),f.y);
  }

  void main() {
    float rVal = texture2D(fbTexture, vUv).r;
    rVal -= clamp(dTime / pointerDuration, 0., 0.05);  // TIME-BASED DECAY
    rVal  = clamp(rVal, 0., 1.);

    float f = 0.0;
    if (pointerDown > 0.5) {
      vec2 uv     = (vUv - 0.5) * 2.0 * vec2(aspect, 1.0);
      vec2 mouse  = pointer * vec2(aspect, 1.0);
      vec2 toMouse = uv - mouse;
      
      // ANGLE-BASED NOISE (KEY DIFFERENCE)
      float angle  = atan(toMouse.y, toMouse.x);
      float dist   = length(toMouse);
      float nv     = noise(vec2(angle*3.0 + time*0.5, dist*5.0));
      float nv2    = noise(vec2(angle*5.0 - time*0.3, dist*3.0 + time));
      float rv     = 0.7 + nv*0.5 + nv2*0.3;
      float or2    = pointerRadius * rv;
      
      f = 1.0 - smoothstep(or2*0.05, or2*1.2, dist);
      f *= 0.8 + nv*0.2;
    }
    rVal += f * 0.25;  // NATURAL BUILDUP
    rVal  = clamp(rVal, 0., 1.);
    gl_FragColor = vec4(rVal, rVal, rVal, 1.0);
  }
`
```

**Why this works instantly:**
1. Time-based decay: `rVal -= clamp(dTime / pointerDuration, 0., 0.05)`
2. Brush adds `0.25 × brushValue` per frame (no multipliers needed)
3. Angle-based noise creates more organic, varied brush shape
4. First frame with `f = 0.8` → `rVal = 0.2` (immediately visible)
5. Result: Instant reveal, no perceptible delay

---

## 🔧 THE FIX APPLIED

Master Chat replaced your Three.js shader with the **EXACT wireframe code**.

**Changes made:**

### 1. Uniforms Structure (Lines 42-48)
**Before:**
```typescript
const gu = {
  aspect: { value: W / H },
  mousePos: { value: new THREE.Vector2(-9999, -9999) },
  mouseVel: { value: new THREE.Vector2(0, 0) },
  pointerAlpha: { value: 0 },
  time: { value: 0 },
  dTime: { value: 0 },
};
```

**After:**
```typescript
const gu = {
  time: { value: 0 },
  dTime: { value: 0 },
  aspect: { value: W / H },
};

const blobUniforms = {
  pointer: { value: new THREE.Vector2().setScalar(10) },
  pointerDown: { value: 1 },
  pointerRadius: { value: POINTER_RADIUS },
  pointerDuration: { value: POINTER_DURATION },
};
```

### 2. Event Handlers (Lines 51-58)
**Before:**
```typescript
wrap.addEventListener("mouseenter", (e) => {
  isHovering = true;
  hoverStartTime = performance.now() / 1000;
  const rect = wrap.getBoundingClientRect();
  const mx = ((e.clientX - rect.left) / W) * 2 - 1;
  const my = -(((e.clientY - rect.top) / H) * 2 - 1);
  gu.mousePos.value.set(mx, my);
  gu.pointerAlpha.value = 1.0;
});
```

**After:**
```typescript
wrap.addEventListener('mousemove', (e) => {
  const rect = wrap.getBoundingClientRect();
  blobUniforms.pointer.value.x = ((e.clientX - rect.left) / W) * 2 - 1;
  blobUniforms.pointer.value.y = -((e.clientY - rect.top) / H) * 2 + 1;
});

wrap.addEventListener('mouseleave', () => {
  blobUniforms.pointer.value.setScalar(10);
});
```

### 3. Shader Material Uniforms (Lines 71-80)
**Before:**
```typescript
uniforms: {
  fbTexture: { value: null },
  aspect: gu.aspect,
  mousePos: gu.mousePos,
  mouseVel: gu.mouseVel,
  pointerAlpha: gu.pointerAlpha,
  time: gu.time,
  dTime: gu.dTime,
  pointerRadius: { value: POINTER_RADIUS },
}
```

**After:**
```typescript
uniforms: {
  dTime: gu.dTime,
  aspect: gu.aspect,
  pointer: blobUniforms.pointer,
  pointerDown: blobUniforms.pointerDown,
  pointerRadius: blobUniforms.pointerRadius,
  pointerDuration: blobUniforms.pointerDuration,
  fbTexture: { value: null },
  time: gu.time,
}
```

### 4. Fragment Shader (Lines 91-127)
**Entire algorithm replaced with wireframe's angle-based approach**

See comparison above for detailed differences.

### 5. Animation Loop (Lines 336-342)
**Before:**
```typescript
if (!isHovering) {
  gu.pointerAlpha.value = Math.max(gu.pointerAlpha.value - dt * 3.0, 0);
}
```

**After:**
```typescript
// No fade-out logic needed - shader handles decay automatically
renderBlob();
```

---

## 📋 NEW HERO.TSX PROVIDED

Christopher will upload the corrected `Hero.tsx` file to you.

**File location:** `components/Hero.tsx`

**What it contains:**
- ✅ EXACT wireframe Three.js code (lines 735-990 from approved wireframe)
- ✅ Angle-based noise shader algorithm
- ✅ Time-based decay
- ✅ Simplified event handlers
- ✅ All 3 layers (base image, liquid bg, robot reveal)
- ✅ Resize handling
- ✅ Loading state
- ✅ React hooks integration

**What you must NOT change:**
- ❌ The blob shader fragmentShader (lines 91-127)
- ❌ The event handlers (lines 51-58)
- ❌ The uniforms structure (lines 42-48, 71-80)
- ❌ Any Three.js rendering logic

---

## ✅ VERIFICATION QUESTIONS

**Before you continue building the website, you MUST answer these 5 questions to prove you understand the fix.**

Send your answers to Master Chat in this format:

```
HERO FIX VERIFICATION ANSWERS

Q1: [Your answer]
Q2: [Your answer]
Q3: [Your answer]
Q4: [Your answer]
Q5: [Your answer]

Awaiting Master Chat approval to proceed.
```

---

### **Q1: Shader Algorithm**
**Question:** What is the fundamental difference between the old shader algorithm and the new wireframe shader algorithm? (Answer in 2-3 sentences max)

**What Master Chat is looking for:**
- Mention of angle-based vs distance-based approach
- Recognition that wireframe uses `atan()` for angle calculation
- Understanding of dual noise layers (`nv` and `nv2`)

---

### **Q2: Decay Mechanism**
**Question:** How does the wireframe shader handle decay differently than the old implementation? Quote the exact line of code.

**What Master Chat is looking for:**
- The line: `rVal -= clamp(dTime / pointerDuration, 0., 0.05);`
- Recognition that it's time-based, not state-based
- Understanding that this happens every frame regardless of hover state

---

### **Q3: Event Handlers**
**Question:** The old implementation had `mouseenter` and `mouseleave` with hover state tracking. What does the wireframe use instead and why is it simpler?

**What Master Chat is looking for:**
- Wireframe uses only `mousemove` and `mouseleave`
- No `isHovering` state needed
- Pointer position updated directly in `blobUniforms.pointer`

---

### **Q4: Instant Reveal**
**Question:** Why does the wireframe shader reveal instantly while the old shader had a fade-in delay? Explain the math.

**What Master Chat is looking for:**
- Old shader: brush × 4.0, but needs to overcome 0.92 decay over multiple frames
- Wireframe: adds `f * 0.25` where `f` can be 0.8 on first frame
- First frame `rVal = 0.2` is immediately visible (20% brightness)

---

### **Q5: What NOT to Change**
**Question:** You're about to continue building the website. List 3 specific sections of the new Hero.tsx that you must NEVER modify, even if you think you can "improve" them.

**What Master Chat is looking for:**
- The blob shader fragmentShader (lines 91-127)
- The angle-based noise calculation
- The uniforms structure and event handlers
- Any acknowledgment that the Three.js code is LOCKED and approved

---

## 🎯 NEXT STEPS

1. **Christopher uploads new Hero.tsx** to you
2. **You read and analyze** the new Hero.tsx code
3. **You answer the 5 verification questions** above
4. **Master Chat reviews your answers**
5. **IF approved:** Continue building the remaining 12 sections (S2-S13)
6. **IF not approved:** Master Chat will clarify until you understand

---

## ⚠️ CRITICAL REMINDERS

**DO NOT:**
- ❌ Modify the Three.js shader code "to make it better"
- ❌ Change the event handlers "for consistency"
- ❌ Refactor the uniforms structure "to be cleaner"
- ❌ Add comments or optimizations to the shader
- ❌ Assume you know better than the approved wireframe

**DO:**
- ✅ Use the new Hero.tsx EXACTLY as provided
- ✅ Build the remaining 12 sections (AboutMe through Footer)
- ✅ Follow the brief's specifications for those sections
- ✅ Test everything thoroughly
- ✅ Provide complete files in outputs directory

---

## 📚 REFERENCE FILES

**You should have:**
1. ✅ CHAT_31_BRIEF.md (original specifications)
2. ✅ CHAT_31_WIREFRAME_LIGHTWEIGHT.html (reference design)
3. ✅ chris_headshot_1.jpg (headshot image)
4. ✅ ACT_headshot_1.jpg (robot image)
5. ✅ **Hero.tsx (NEW - corrected version from Master Chat)**

**Read the new Hero.tsx carefully before answering the verification questions.**

---

**Version:** 1.0
**Last Updated:** 2026-02-23
**Approved by:** Master Chat 4.0

**END OF BRIEFING**
