from pico2d import get_time, load_image
import pico2d.pico2d as pico2d_core
from transitions import Machine


class Boy:
    INVINCIBLE_RUN_DURATION = 5.0
    INVINCIBLE_RUN_SPEED = 6

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.idle_started = get_time()
        self.invincible_started = None
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['idle', 'run', 'sleep', 'invincible_run'],
            initial='idle',
        )
        self.machine.add_transition('fall_asleep', 'idle', 'sleep')
        self.machine.add_transition('wake_up', 'sleep', 'idle', after='reset_idle_time')
        self.machine.add_transition('start_run', 'idle', 'run')
        self.machine.add_transition('stop_run', 'run', 'idle', after='reset_idle_time')
        self.machine.add_transition('override_invincible_run', 'invincible_run', 'run')
        self.machine.add_transition(
            'start_invincible_run', ['idle', 'run', 'sleep'], 'invincible_run',
            after='mark_invincible_run_started',
        )

    def mark_invincible_run_started(self):
        self.invincible_started = get_time()

    def reset_idle_time(self):
        self.idle_started = get_time()

    def handle_event(self, event):
        from pico2d import (
            SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_a,
        )

        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_a and self.state != 'invincible_run':
                self.start_invincible_run()
            elif self.state == 'sleep' and event.key == SDLK_SPACE:
                self.wake_up()
            elif event.key in (SDLK_LEFT, SDLK_RIGHT):
                self.face_dir = -1 if event.key == SDLK_LEFT else 1
                if self.state == 'sleep':
                    self.wake_up()
                if self.state == 'idle':
                    self.start_run()
        elif event.type == SDL_KEYUP and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if self.state == 'run':
                self.stop_run()

    def update(self):
        if self.state == 'idle':
            if get_time() - self.idle_started >= 5.0:
                self.fall_asleep()
                return
            self.frame = (self.frame + 1) % 8
        elif self.state == 'run':
            self.x += self.face_dir * 3
            self.x = max(0, min(800, self.x))
            self.frame = (self.frame + 1) % 8
        elif self.state == 'invincible_run':
            self.x += self.face_dir * self.INVINCIBLE_RUN_SPEED
            self.x = max(0, min(800, self.x))
            if self.x == 800 and self.face_dir > 0:
                self.face_dir = -1
            elif self.x == 0 and self.face_dir < 0:
                self.face_dir = 1
            self.frame = (self.frame + 1) % 8

    def draw(self):
        if self.state == 'sleep':
            # clip_draw in this pico2d version has no rotation argument.
            src = pico2d_core.SDL_Rect(
                0, self.image.h - (300 if self.face_dir == 1 else 200) - 100, 100, 100
            )
            sleep_y = self.y - 25
            dest = pico2d_core.to_sdl_rect(self.x - 50, sleep_y - 50, 100, 100)
            sleep_rotation = 270 if self.face_dir == 1 else 90
            pico2d_core.SDL_RenderCopyEx(
                pico2d_core.renderer, self.image.texture, src, dest,
                sleep_rotation, None, pico2d_core.SDL_FLIP_NONE,
            )
        elif self.state == 'run' and self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 100, 100, 100, self.x, self.y)
        elif self.state == 'run':
            self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)
        elif self.face_dir == 1:
            self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
