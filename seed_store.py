"""Seed the store with starter cosmetic items."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.factories.app_factory import create_app, db
from app.models.tienda import StoreItem

app = create_app('development')

ITEMS = [
    # ── Frames (marcos para avatar) ──
    StoreItem(name='Marco Básico Rojo', category='frame', price=50, stock=999,
              css_class='border: 3px solid #EF4444; box-shadow: 0 0 8px #EF4444;', color_hex='#EF4444'),
    StoreItem(name='Marco Esmeralda', category='frame', price=80, stock=999,
              css_class='border: 3px solid #10B981; box-shadow: 0 0 8px #10B981;', color_hex='#10B981'),
    StoreItem(name='Marco Azul Eléctrico', category='frame', price=80, stock=999,
              css_class='border: 3px solid #3B82F6; box-shadow: 0 0 8px #3B82F6;', color_hex='#3B82F6'),
    StoreItem(name='Marco Rosa Neón', category='frame', price=120, stock=500,
              css_class='border: 3px solid #FF2D95; box-shadow: 0 0 12px #FF2D95;', color_hex='#FF2D95'),
    StoreItem(name='Marco Dorado Premium', category='frame', price=200, stock=200,
              css_class='border: 3px solid #FACC15; box-shadow: 0 0 15px #FACC15;', color_hex='#FACC15'),
    StoreItem(name='Marco Púrpura Legendario', category='frame', price=300, stock=100,
              css_class='border: 3px solid #A78BFA; box-shadow: 0 0 20px #A78BFA;', color_hex='#A78BFA'),
    StoreItem(name='Marco Cian Esencia', category='frame', price=150, stock=300,
              css_class='border: 3px solid #22D3EE; box-shadow: 0 0 12px #22D3EE;', color_hex='#22D3EE'),
    StoreItem(name='Marco Fuego', category='frame', price=250, stock=150,
              css_class='border: 3px solid #F97316; box-shadow: 0 0 15px #F97316;', color_hex='#F97316'),
    StoreItem(name='Marco Dragón', category='frame', price=400, stock=50,
              css_class='border: 3px solid #DC2626; box-shadow: 0 0 20px #DC2626, inset 0 0 10px #DC2626;', color_hex='#DC2626'),
    StoreItem(name='Marco Hielo', category='frame', price=180, stock=250,
              css_class='border: 3px solid #67E8F9; box-shadow: 0 0 12px #67E8F9;', color_hex='#67E8F9'),

    # ── Backgrounds (fondos/banners) ──
    StoreItem(name='Atardecer Pixelado', category='background', price=100, stock=999,
              image_url='https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&fit=crop', color_hex='#F59E0B'),
    StoreItem(name='Nebulosa Galáctica', category='background', price=150, stock=500,
              image_url='https://images.unsplash.com/photo-1543722530-d2c3201371e7?w=600&fit=crop', color_hex='#7C3AED'),
    StoreItem(name='Selva Mística', category='background', price=120, stock=500,
              image_url='https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=600&fit=crop', color_hex='#059669'),
    StoreItem(name='Ciudad Cyberpunk', category='background', price=200, stock=300,
              image_url='https://images.unsplash.com/photo-1605806616949-1e87b487cb2a?w=600&fit=crop', color_hex='#FF2D95'),
    StoreItem(name='Amanecer en la Montaña', category='background', price=80, stock=999,
              image_url='https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&fit=crop', color_hex='#F97316'),
    StoreItem(name='Espacio Profundo', category='background', price=250, stock=200,
              image_url='https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=600&fit=crop', color_hex='#1E3A8A'),
    StoreItem(name='Arena del Desierto', category='background', price=90, stock=999,
              image_url='https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=600&fit=crop', color_hex='#D97706'),
    StoreItem(name='Océano Nocturno', category='background', price=180, stock=400,
              image_url='https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=600&fit=crop', color_hex='#1D4ED8'),

    # ── Titles (títulos de perfil) ──
    StoreItem(name='Cazador de Leyendas', category='title', price=150, stock=999,
              css_class='color: #EF4444; font-weight: 900; text-shadow: 0 0 8px #EF4444;', color_hex='#EF4444'),
    StoreItem(name='Maestro del Caos', category='title', price=180, stock=500,
              css_class='color: #A78BFA; font-weight: 900; text-shadow: 0 0 8px #A78BFA;', color_hex='#A78BFA'),
    StoreItem(name='Dios del Aim', category='title', price=220, stock=300,
              css_class='color: #22D3EE; font-weight: 900; text-shadow: 0 0 10px #22D3EE;', color_hex='#22D3EE'),
    StoreItem(name='Velocidad Pura', category='title', price=130, stock=500,
              css_class='color: #10B981; font-weight: 900; text-shadow: 0 0 8px #10B981;', color_hex='#10B981'),
    StoreItem(name='Rey de la Partida', category='title', price=280, stock=150,
              css_class='color: #FACC15; font-weight: 900; text-shadow: 0 0 12px #FACC15;', color_hex='#FACC15'),
    StoreItem(name='Sombras Eternas', category='title', price=200, stock=300,
              css_class='color: #6B7280; font-weight: 900; text-shadow: 0 0 8px #6B7280;', color_hex='#6B7280'),
    StoreItem(name='Llamarada', category='title', price=160, stock=500,
              css_class='color: #F97316; font-weight: 900; text-shadow: 0 0 10px #F97316;', color_hex='#F97316'),
    StoreItem(name='Alma de Diamante', category='title', price=350, stock=100,
              css_class='color: #67E8F9; font-weight: 900; text-shadow: 0 0 15px #67E8F9;', color_hex='#67E8F9'),
]

with app.app_context():
    existing = StoreItem.query.count()
    if existing > 0:
        print(f"La tienda ya tiene {existing} artículos. No se agregaron duplicados.")
    else:
        for item in ITEMS:
            db.session.add(item)
        db.session.commit()
        print(f"OK {len(ITEMS)} articulos agregados a la tienda:")
        for item in ITEMS:
            print(f"  - [{item.category}] {item.name} - {item.price} RC")
