let SessionLoad = 1
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/python_projects/relay_ft245r
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +0 ~/python_projects/relay_ft245r/test.py
badd +158 ~/python_projects/relay_ft245r/relay_ft245r.py
badd +0 term://~/python_projects/relay_ft245r//11817:python\ test.py
badd +8 term://~/python_projects/relay_ft245r//11823:python\ test.py
badd +311 ~/miniconda3/lib/python3.7/site-packages/usb/util.py
badd +5 ~/python_projects/relay_ft245r/blinking.py
badd +3 ~/python_projects/relay_ft245r/scratch_pad.py
badd +0 ~/python_projects/relay_ft245r/TODO
argglobal
%argdel
$argadd test.py
edit ~/python_projects/relay_ft245r/relay_ft245r.py
set splitbelow splitright
wincmd t
set winminheight=0
set winheight=1
set winminwidth=0
set winwidth=1
argglobal
setlocal fdm=expr
setlocal fde=SimpylFold#FoldExpr(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
75
normal! zo
185
normal! zo
187
normal! zo
189
normal! zo
190
normal! zo
let s:l = 189 - ((114 * winheight(0) + 24) / 49)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
189
normal! 09|
tabnext 1
if exists('s:wipebuf') && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 winminheight=1 winminwidth=1 shortmess=filnxtToOF
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
