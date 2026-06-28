# -*- coding: utf-8 -*-
# 雑魚敵（響妖）のスプライトを生成 → 透過＆ダウンスケール
import io, numpy as np
from huggingface_hub import InferenceClient
from PIL import Image

TOKEN="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"
client=InferenceClient(token=TOKEN)
prompt=("a small cute floating spirit wisp enemy for a danmaku shooter, single glowing "
        "pale cyan-white orb creature with tiny translucent wings and a soft musical-note glow, "
        "chibi, centered, plain dark background, soft bloom, clean game sprite, front view")
img=client.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell",
                         width=512, height=512, seed=7777)
img=img.convert("RGBA")
# 楕円フェザー透過（中心を残して周辺を抜く）＋暗部も抜く
a=np.array(img).astype(np.float32)
h,w=a.shape[:2]
yy,xx=np.mgrid[0:h,0:w]
cx,cy=w/2,h/2
r=np.sqrt(((xx-cx)/(w*0.46))**2+((yy-cy)/(h*0.46))**2)
mask=np.clip(1.0-(r-0.7)/0.3,0,1)            # 周辺フェザー
lum=a[:,:,:3].mean(2)/255.0
mask=mask*np.clip((lum-0.10)/0.30,0,1)        # 暗い背景を抜く
a[:,:,3]=(a[:,:,3]*mask).clip(0,255)
out=Image.fromarray(a.astype(np.uint8))
out=out.resize((72,72), Image.LANCZOS)
out.save("/tmp/zako.png")
print("saved /tmp/zako.png", out.size)
