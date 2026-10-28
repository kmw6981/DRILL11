from pico2d import *
from boy import Boy
from grass import Grass

# 1. 화면 크기 설정 및 캔버스 열기
open_canvas(800, 600)

# 2. 게임 초기화 (객체 생성)
running = True
grass = Grass()
boy = Boy()

# 3. 게임 메인 루프
while running:
    # 3-1. 이벤트 처리 (창 닫기 등)
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            boy.handle_event(event)

    # 3-2. 게임 로직 업데이트
    boy.update()
    grass.update()

    # 3-3. 화면 그리기 (렌더링)
    clear_canvas()
    grass.draw()
    boy.draw()
    update_canvas()

    # 3-4. 프레임 속도 조절 (약 60프레임 유지)
    delay(0.01)

# 4. 캔버스 닫기
close_canvas()
