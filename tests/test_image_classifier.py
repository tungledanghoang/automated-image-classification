from src.image_model import ImageClassifierModel


def test_image_classifiers():
    img_classifier_18 = ImageClassifierModel("resnet18")
    labels_18 = img_classifier_18.classify_image_batch(
        ["tests/images/kitchen.jpg", "tests/images/living_room.jpg"])
    img_classifier_34 = ImageClassifierModel("resnet34")
    labels_34 = img_classifier_34.classify_image_batch(
        ["tests/images/kitchen.jpg", "tests/images/living_room.jpg"])
    img_classifier_50 = ImageClassifierModel("resnet50")
    labels_50 = img_classifier_50.classify_image_batch(
        ["tests/images/kitchen.jpg", "tests/images/living_room.jpg"])
    assert len(labels_18) == 2
    assert len(labels_34) == 2
    assert len(labels_50) == 2
    for label in labels_18:
        assert isinstance(label, str)
    for label in labels_34:
        assert isinstance(label, str)
    for label in labels_50:
        assert isinstance(label, str)
