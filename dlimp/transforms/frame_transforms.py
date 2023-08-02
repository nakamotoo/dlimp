from functools import partial
from typing import Any, Dict, Sequence, Tuple, Union

import tensorflow as tf

from dlimp.augmentations import augment_image
from dlimp.utils import resize_image

from .common import selective_tree_map


def decode_images(
    x: Dict[str, Any], match: Union[str, Sequence[str]] = "image"
) -> Dict[str, Any]:
    """Can operate on nested dicts. Decodes any leaves that have `match` anywhere in their path."""
    if isinstance(match, str):
        match = [match]

    return selective_tree_map(
        x,
        lambda keypath, value: any([s in keypath for s in match])
        and value.dtype == tf.string,
        partial(tf.io.decode_image, expand_animations=False),
    )


def resize_images(
    x: Dict[str, Any],
    match: Union[str, Sequence[str]] = "image",
    size: Tuple[int, int] = (128, 128),
) -> Dict[str, Any]:
    """Can operate on nested dicts. Resizes any leaves that have `match` anywhere in their path. Takes uint8 images
    as input and returns float images (still in [0, 255]).
    """
    if isinstance(match, str):
        match = [match]

    return selective_tree_map(
        x,
        lambda keypath, value: any([s in keypath for s in match])
        and value.dtype == tf.uint8,
        partial(resize_image, size=size),
    )


def augment(
    x: Dict[str, Any],
    match: Union[str, Sequence[str]] = "image",
    traj_identical: bool = True,
    augment_kwargs: dict = {},
) -> Dict[str, Any]:
    """
    Augments the input dictionary `x` by applying image augmentation to all values whose keypath contains `match`.

    Args:
        x (Dict[str, Any]): The input dictionary to augment.
        match (str, optional): The string to match in keypaths. Defaults to "image".
        traj_identical (bool, optional): Whether to use the same random seed for all images in a trajectory.
        augment_kwargs (dict, optional): Additional keyword arguments to pass to the `augment_image` function.
    """

    def map_fn(value):
        if traj_identical:
            seed = [x["_traj_index"], x["_traj_index"]]
        else:
            seed = None
        return augment_image(value, seed=seed, **augment_kwargs)

    return selective_tree_map(
        x,
        match,
        map_fn,
    )
