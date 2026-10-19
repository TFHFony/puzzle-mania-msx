; ------------------------------------------------------------------------------------------------ diagnostic build (tools/build_game.py --diag)
; Plays the menu music and measures, for 10 seconds at a time, how much time the player has left in every frame: mvsync returns in mus_sl the number of polls
; of the wait for the blanking (0 = the frame was late; counted by the player itself, see gen_slots.py).  The results stay on the screen; the runs alternate between an idle frame and a frame that is
; announced as an action frame (the longer pause), so that the machine can be compared with openMSX.
        IF DIAG
DCOL    equ 0xF1

diag:   call clrscr
        ld hl,dt0
        ld d,0
        ld e,3
        call dtext
        ld hl,dt1
        ld d,2
        ld e,2
        call dtext
        ld hl,dt2
        ld d,3
        ld e,2
        call dtext
        ld hl,dt3
        ld d,4
        ld e,2
        call dtext
        ld hl,dt4
        ld d,6
        ld e,2
        call dtext
        ld hl,dt5
        ld d,7
        ld e,2
        call dtext
        ld hl,dt6
        ld d,9
        ld e,2
        call dtext
        ld hl,dt7
        ld d,10
        ld e,2
        call dtext
        ld hl,dt8
        ld d,11
        ld e,2
        call dtext
        ld hl,dt9
        ld d,12
        ld e,2
        call dtext
        ld hl,dt10
        ld d,13
        ld e,2
        call dtext
        ld hl,dt14
        ld d,14
        ld e,2
        call dtext
        ld hl,dt11
        ld d,18
        ld e,1
        call dtext
        ld hl,dt12
        ld d,19
        ld e,1
        call dtext
        ld hl,dt13
        ld d,20
        ld e,1
        call dtext
        ld a,(v_hz)
        ld l,a
        ld h,0
        ld d,2
        ld e,18
        call pn
        ld a,(v_hz)                     ; frames of a run: 10 seconds
        ld l,a
        ld h,0
        ld d,h
        ld e,l
        add hl,hl
        add hl,hl
        add hl,de
        add hl,hl
        ld d,3
        ld e,18
        call pn
        xor a
        ld (d_run),a
        ld c,1
        call music_play                 ; the menu music

.run:   ld hl,dt_meas
        ld d,15
        ld e,2
        call dtext
        ld hl,0
        ld (d_late),hl
        ld (d_sum),hl
        ld (d_to),hl
        ld a,255
        ld (d_min),a
        ld a,(v_hz)
        ld l,a
        ld h,0
        ld d,h
        ld e,l
        add hl,hl
        add hl,hl
        add hl,de
        add hl,hl
        ld (d_cnt),hl
.m:     ld a,(d_run)
        and 1
        jr z,.nh
        ld a,2                          ; odd runs: every frame is an action frame
        ld (mus_hint),a
.nh:    call mvsync
        ld hl,(d_cnt)
        dec hl
        ld (d_cnt),hl
        ld a,h
        or l
        jr nz,.m
        ; ---- results
        ld hl,dt_done
        ld d,15
        ld e,2
        call dtext
        ld a,(d_run)
        ld l,a
        ld h,0
        ld d,6
        ld e,18
        call pn
        ld hl,dt_idle
        ld a,(d_run)
        and 1
        jr z,.md
        ld hl,dt_act
.md:    ld d,7
        ld e,18
        call dtext
        ld hl,(d_late)
        ld d,9
        ld e,18
        call pn
        ld a,(d_min)
        cp 255                          ; every frame was late
        jr nz,.pm
        xor a
.pm:    ld l,a
        ld h,0
        ld d,10
        ld e,18
        call pn
        ld a,(v_hz)                     ; average x 10 = sum / hz
        ld e,a
        ld d,0
        ld hl,(d_sum)
        ld bc,0
.dv:    or a
        sbc hl,de
        jr c,.dn
        inc bc
        jr .dv
.dn:    ld h,b
        ld l,c
        ld d,11
        ld e,18
        call pn
        ld a,(mus_n)
        ld l,a
        ld h,0
        ld d,12
        ld e,18
        call pn
        ld a,(mus_sk)
        ld l,a
        ld h,0
        ld d,13
        ld e,18
        call pn
        ld hl,(d_to)
        ld d,14
        ld e,18
        call pn
        ld hl,d_run
        inc (hl)
        jp .run

pn:     push de                         ; HL = number, D = row, E = column (the old digits are overwritten)
        ld de,d_buf
        call dec16
        ld a,' '
        ld (de),a
        inc de
        ld (de),a
        inc de
        ld (de),a
        inc de
        xor a
        ld (de),a
        pop de
        ld hl,d_buf
dtext:  ld a,DCOL
        jp text

dt0:    db "DIAGNOSTIC",0
dt1:    db "HZ:",0
dt2:    db "FRAMES PER RUN:",0
dt3:    db "RUN TIME: 10 SECONDS",0
dt4:    db "RUN:",0
dt5:    db "MODE:",0
dt6:    db "LATE FRAMES:",0
dt7:    db "SLACK MIN:",0
dt8:    db "SLACK AVG X10:",0
dt9:    db "SAMPLES/FRAME:",0
dt10:   db "SKIPPED:",0
dt11:   db "SLACK = POLLS TO THE BLANKING",0
dt12:   db "LATE FRAMES SHOULD BE 0",0
dt13:   db "TIME A RUN WITH A STOPWATCH",0
dt14:   db "TIMEOUTS:",0
dt_meas: db "MEASURING...  ",0
dt_done: db "DONE.         ",0
dt_idle: db "IDLE  ",0
dt_act:  db "ACTION",0
        ENDIF
