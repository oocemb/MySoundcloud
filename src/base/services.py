import os
from django.core.exceptions import ValidationError


def get_path_upload_avatar(instanse,file):
    """Генерация пути к файлу аватара пользователя (media)/avatar/user_id/photo.jpg"""
    return f'avatar/{instanse.id}/{file}'


def get_path_upload_cover_track(instanse,file):
    """Генерация пути к файлу обложки альбома (media)/track_cover/user_id/photo.jpg"""
    return f'track_cover/user_{instanse.user.id}/{file}'


def get_path_upload_cover_album(instanse,file):
    """Генерация пути к файлу обложки альбома (media)/album/user_id/photo.jpg"""
    return f'album/user_{instanse.user.id}/{file}'


def get_path_upload_cover_playlist(instanse,file):
    """Генерация пути к файлу обложки плэйлиста (media)/playlist/user_id/photo.jpg"""
    return f'playlist/user_{instanse.user.id}/{file}'


def get_path_upload_track(instanse,file):
    """Генерация пути к файлу трэка (media)/track/user_id/photo.jpg"""
    return f'track/user_{instanse.user.id}/{file}'


def validate_size_image(file_obj):
    """Проверка размера файла"""
    megabyte_limit = 2
    if file_obj.size > megabyte_limit * 1024 * 1024:
        raise ValidationError(f"Максимальный размер файла {megabyte_limit} MB")


def delete_old_file(path_file):
    """Удаление старого файла"""
    if os.path.exists(path_file):
        os.remove(path_file)