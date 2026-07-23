"""Node subclasses wrapping core processing functions."""
import numpy as np
from core.node_graph import Node, Socket
from core.color_correction_nodes import (
    node_color_balance_lgg, node_color_balance_cdl,
    node_brightness_contrast, node_exposure,
    node_hue_saturation_value, node_gamma,
    node_invert, node_posterize, node_color_correction_3way,
)
from core.curves_nodes import node_rgb_curves, node_hue_correct, node_float_curve
from core.keying_nodes import (
    node_color_key, node_chroma_key, node_difference_key,
    node_luminance_key, node_channel_key, node_distance_key,
    node_color_spill, node_keying,
)
from core.additional_nodes import (
    node_tonemap_reinhard, node_tonemap_photoreceptor,
    node_alpha_over, node_alpha_set,
    node_levels, node_combine_color, node_separate_color,
    node_convert_colorspace, node_pixelate,
    node_shadows_highlights, node_color_temperature,
    node_split_toning, node_vignette, node_film_grain,
    node_blur, node_glow, node_sharpen,
)
from core.blend_modes import blend, BLEND_MODES


class ColorBalanceLGGNode(Node):
    def __init__(self, label=""):
        super().__init__("color_balance_lgg", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'lift': [0,0,0], 'gamma': [1,1,1], 'gain': [1,1,1], 'offset': [0,0,0], 'factor': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_color_balance_lgg(img, **self.params)


class ColorBalanceCDLNode(Node):
    def __init__(self, label=""):
        super().__init__("color_balance_cdl", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'slope': [1,1,1], 'offset': [0,0,0], 'power': [1,1,1], 'factor': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_color_balance_cdl(img, **self.params)


class BrightnessContrastNode(Node):
    def __init__(self, label=""):
        super().__init__("brightness_contrast", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'brightness': 0.0, 'contrast': 0.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_brightness_contrast(img, **self.params)


class ExposureNode(Node):
    def __init__(self, label=""):
        super().__init__("exposure", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'exposure': 0.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_exposure(img, **self.params)


class HueSaturationValueNode(Node):
    def __init__(self, label=""):
        super().__init__("hue_saturation_value", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'hue': 0.0, 'saturation': 0.0, 'value': 0.0, 'factor': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_hue_saturation_value(img, **self.params)


class GammaNode(Node):
    def __init__(self, label=""):
        super().__init__("gamma", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'gamma': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_gamma(img, **self.params)


class InvertNode(Node):
    def __init__(self, label=""):
        super().__init__("invert", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'factor': 1.0, 'invert_color': True, 'invert_alpha': False}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_invert(img, **self.params)


class PosterizeNode(Node):
    def __init__(self, label=""):
        super().__init__("posterize", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'steps': 32}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_posterize(img, **self.params)


class RGBCurvesNode(Node):
    def __init__(self, label=""):
        super().__init__("rgb_curves", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'curves': None, 'black_level': [0,0,0], 'white_level': [1,1,1], 'factor': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_rgb_curves(img, **self.params)


class HueCorrectNode(Node):
    def __init__(self, label=""):
        super().__init__("hue_correct", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'curves': None, 'factor': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_hue_correct(img, **self.params)


class TonemapNode(Node):
    def __init__(self, label=""):
        super().__init__("tonemap", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'key': 0.18, 'offset': 0.0, 'gamma': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_tonemap_reinhard(img, **self.params)


class AlphaOverNode(Node):
    def __init__(self, label=""):
        super().__init__("alpha_over", label)
        self.inputs = [Socket("Image", "color"), Socket("Overlay", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'premul': True, 'factor': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        ov = inputs.get("Overlay", np.zeros((1,1,3)))
        return node_alpha_over(img, ov, **self.params)


class LevelsNode(Node):
    def __init__(self, label=""):
        super().__init__("levels", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'channel': 0, 'in_min': 0.0, 'in_max': 1.0,
                       'out_min': 0.0, 'out_max': 1.0, 'gamma': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_levels(img, **self.params)


class KeyingNode(Node):
    def __init__(self, label=""):
        super().__init__("keying", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'key_color': np.array([0,1,0]), 'balance': 0.5,
                       'black_level': 0.0, 'white_level': 1.0,
                       'despill_strength': 0.5, 'despill_balance': 0.5}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_keying(img, **self.params)


class ColorSpillNode(Node):
    def __init__(self, label=""):
        super().__init__("color_spill", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'spill_channel': 0, 'limit_method': 'single',
                       'limit_channel': 0, 'limit_strength': 1.0, 'factor': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_color_spill(img, **self.params)


class BlendNode(Node):
    def __init__(self, label=""):
        super().__init__("blend", label)
        self.inputs = [Socket("Image", "color"), Socket("Blend", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'mode': 'mix', 'fac': 0.5}
    def process(self, inputs):
        a = inputs.get("Image", np.zeros((1,1,3)))
        b = inputs.get("Blend", np.zeros((1,1,3)))
        return blend(self.params['mode'], a, b, self.params['fac'])


class PixelateNode(Node):
    def __init__(self, label=""):
        super().__init__("pixelate", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'size': 10}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_pixelate(img, **self.params)


class ShadowsHighlightsNode(Node):
    def __init__(self, label=""):
        super().__init__("shadows_highlights", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'shadows': 0.0, 'highlights': 0.0, 'shadow_tone': 0.5,
                       'highlight_tone': 0.5, 'color_correction': 0.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_shadows_highlights(img, **self.params)


class ColorTemperatureNode(Node):
    def __init__(self, label=""):
        super().__init__("color_temperature", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'temperature': 6500.0, 'tint': 0.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_color_temperature(img, **self.params)


class SplitToningNode(Node):
    def __init__(self, label=""):
        super().__init__("split_toning", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'shadow_color': (0.5, 0.5, 0.6), 'highlight_color': (0.6, 0.5, 0.4),
                       'balance': 0.0, 'factor': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_split_toning(img, **self.params)


class VignetteNode(Node):
    def __init__(self, label=""):
        super().__init__("vignette", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'strength': 0.5, 'size': 0.8, 'feather': 0.4,
                       'center_x': 0.5, 'center_y': 0.5}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_vignette(img, **self.params)


class FilmGrainNode(Node):
    def __init__(self, label=""):
        super().__init__("film_grain", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'amount': 0.1, 'size': 1.0, 'seed': 0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_film_grain(img, **self.params)


class BlurNode(Node):
    def __init__(self, label=""):
        super().__init__("blur", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'size': 5, 'sigma': 1.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_blur(img, **self.params)


class GlowNode(Node):
    def __init__(self, label=""):
        super().__init__("glow", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'threshold': 0.8, 'softness': 0.5, 'intensity': 0.5, 'size': 21}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_glow(img, **self.params)


class SharpenNode(Node):
    def __init__(self, label=""):
        super().__init__("sharpen", label)
        self.inputs = [Socket("Image", "color")]
        self.outputs = [Socket("Image", "color")]
        self.params = {'amount': 1.0, 'radius': 1.0, 'threshold': 0.0}
    def process(self, inputs):
        img = inputs.get("Image", np.zeros((1,1,3)))
        return node_sharpen(img, **self.params)


NODE_CLASSES = {
    "color_balance_lgg": ColorBalanceLGGNode,
    "color_balance_cdl": ColorBalanceCDLNode,
    "brightness_contrast": BrightnessContrastNode,
    "exposure": ExposureNode,
    "hue_saturation_value": HueSaturationValueNode,
    "gamma": GammaNode,
    "invert": InvertNode,
    "posterize": PosterizeNode,
    "rgb_curves": RGBCurvesNode,
    "hue_correct": HueCorrectNode,
    "tonemap": TonemapNode,
    "alpha_over": AlphaOverNode,
    "levels": LevelsNode,
    "keying": KeyingNode,
    "color_spill": ColorSpillNode,
    "blend": BlendNode,
    "pixelate": PixelateNode,
    "shadows_highlights": ShadowsHighlightsNode,
    "color_temperature": ColorTemperatureNode,
    "split_toning": SplitToningNode,
    "vignette": VignetteNode,
    "film_grain": FilmGrainNode,
    "blur": BlurNode,
    "glow": GlowNode,
    "sharpen": SharpenNode,
}


def create_node(node_type: str, label: str = "") -> Node:
    cls = NODE_CLASSES.get(node_type)
    if cls is None:
        raise ValueError(f"Unknown node type: {node_type}")
    return cls(label)
