import vapoursynth as vs
from vapoursynth import core

core = vs.core
clip = video_in

# ====== 配置参数 ======
SHIFT_X = -1.0    # 水平位移量（正数=右移）
SHIFT_Y = -0.5    # 垂直位移量（正数=下移，负数=上移）

# ====== RGB处理流程 ======
# 转换为 RGB 格式（假设输入为 BT.709）
rgb = core.resize.Bilinear(
    clip,
    format=vs.RGBS,
    matrix_in_s="709" if clip.format.color_family == vs.YUV else "rgb"
)

# 分离 RGB 通道
r, g, b = core.std.SplitPlanes(rgb)

# ====== 蓝色通道位移处理 ======
# 水平+垂直联合位移
shifted_b = core.resize.Bilinear(
    b,
    src_left   = -SHIFT_X,          # 右移1像素（负值=向右采样）
    src_top    = -abs(SHIFT_Y),     # 上移0.5像素（负值=向上采样）
    src_width  = b.width + SHIFT_X, # 扩展采样区域
    src_height = b.height + abs(SHIFT_Y),
    width      = b.width,           # 输出尺寸不变
    height     = b.height,
    filter_param_a=0, filter_param_b=0.5  # 最近邻插值
)

# ====== 重组通道 ======
shifted_clip = core.std.ShufflePlanes(
    clips=[r, g, shifted_b],
    planes=[0, 0, 0],
    colorfamily=vs.RGB
)

# ====== 转回YUV格式 ======
yuv_clip = core.resize.Bicubic(
    shifted_clip,
    format=vs.YUV420P10,
    matrix_s="709",
    dither_type="error_diffusion"
)

yuv_clip.set_output()
