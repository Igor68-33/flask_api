from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app import db, bcrypt
from app.models import Ad
from app.models import User

api = Blueprint('api', __name__)


# ADS
# 1	Объявления все открытый GET	http://127.0.0.1:8000/api/advs/
@api.route('/api/advs/', methods=['GET'])
def get_ads():
    ads = Ad.query.all()
    return jsonify([ad.to_dict() for ad in ads])


# 2	Объявление id открытый GET	http://127.0.0.1:8000/api/adv/<ad_id>
@api.route('/api/adv/<int:ad_id>', methods=['GET'])
def get_ad(ad_id):
    ad = Ad.query.get(ad_id)
    if ad:
        return jsonify(ad.to_dict())
    return jsonify({'message': 'Ad not found'}), 404


# 3	Создать свое закрыт POST	http://127.0.0.1:8000/api/adv/
@api.route('/api/adv/', methods=['POST'])
@jwt_required()  # Если требуется авторизация
def add_ad():
    cur_user_id = get_jwt_identity()
    user = User.query.get(cur_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    new_ad_data = request.get_json()
    if not new_ad_data:
        return jsonify({"error": "No data provided!"}), 400

    # Проверка на наличие необходимых полей
    required_fields = ['title', 'category', 'price', 'description']
    for field in required_fields:
        if field not in new_ad_data or new_ad_data[field] is None:
            return jsonify({"error": f"Missing field: {field}!"}), 400
    ad = Ad()
    for field in required_fields:
        setattr(ad, field, new_ad_data[field])
    ad.user_id = cur_user_id

    db.session.add(ad)
    db.session.commit()

    return jsonify({"message": "Advertisement added successfully!", "ad": ad.to_dict()}), 201


# 4	Изменить свое закрыт PUT	http://127.0.0.1:8000/api/adv/<ad_id>
@api.route('/api/adv/<int:ad_id>', methods=['PUT'])
@jwt_required()
def update_ad(ad_id):
    cur_user_id = get_jwt_identity()
    user = User.query.get(cur_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    ad = Ad.query.get(ad_id)
    if not ad:
        return jsonify({'message': 'Ad not found'}), 404

    if ad.user_id != user.id:
        return jsonify({'message': 'You do not have permission to edit this ad.'}), 403

    update_data = request.get_json()
    if not update_data:
        return jsonify({'message': 'No data provided'}), 400

    allowed_fields = ['title', 'category', 'price', 'description']
    for field in allowed_fields:
        if field in update_data:
            setattr(ad, field, update_data[field])

    db.session.commit()
    return jsonify(ad.to_dict()), 200


# 5	Удалить свое закрыт DEL	http://127.0.0.1:8000/api/adv/<ad_id>
@api.route('/api/adv/<int:ad_id>', methods=['DELETE'])
@jwt_required()
def delete_ad(ad_id):
    cur_user_id = get_jwt_identity()
    user = User.query.get(cur_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    ad = Ad.query.get(ad_id)
    if not ad:
        return jsonify({'message': 'Ad not found'}), 404

    if ad.user_id != user.id:
        return jsonify({'message': f'You do not have  permission to edit this Ad.'}), 403

    db.session.delete(ad)
    db.session.commit()
    return jsonify({'message': 'Ad deleted'})


# USERS

# 1	Пользователи все открыт GET	http://127.0.0.1:8000/api/users/
@api.route('/api/users/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


# 2	Объявления пользователя id открыт GET	http://127.0.0.1:8000/api/user/<user_id>/advs/
@api.route('/api/user/<int:user_id>/advs', methods=['GET'])
def get_ads_user_id(user_id):
    ads = Ad.query.filter_by(user_id=user_id).all()
    return jsonify([ad.to_dict() for ad in ads])


# 3	Защищённый GET self		http://127.0.0.1:8000/api/user/protected/
@api.route('/api/user/protected/', methods=['GET'])
@jwt_required()
def protected():
    cur_user_id = get_jwt_identity()
    user = User.query.get(cur_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'id': user.id, 'username': user.username, 'email': user.email, 'phone': user.phone,
                    'first_name': user.first_name, 'last_name': user.last_name})


# 4	Пользователь id открыт GET	http://127.0.0.1:8000/api/user/<user_id>/
@api.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({'message': 'User  not found'}), 404


# 5	Изменить свою закрыт PUT	http://127.0.0.1:8000/api/user/
@api.route('/api/user/', methods=['PUT'])
@jwt_required()
def update_user():
    cur_user_id = get_jwt_identity()
    user = User.query.get(cur_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
            if key == "password":
                user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    db.session.commit()
    return jsonify(user.to_dict())


# 6	Удалить свою закрыт DEL		http://127.0.0.1:8000/api/user/
@api.route('/api/user/', methods=['DELETE'])
@jwt_required()
def delete_user():
    cur_user_id = get_jwt_identity()
    user = User.query.get(cur_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully.'})


# 7	Регистрация открыт POST		http://127.0.0.1:8000/api/user/register/
@api.route('/api/user/register/', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"message": "User  already exists"}), 400
    if first_name is None or last_name is None or phone is None:
        return jsonify({"message": "Missing  first_name or last_name or phone"}), 400
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password=hashed_password,
                first_name=first_name, last_name=last_name, phone=phone)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': f"{user.id}"}), 201


# 8	Авторизация открыт POST		http://127.0.0.1:8000/api/token/login/
@api.route('/api/token/login/', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401


# 9	Рефреш-токен закрыт POST	http://127.0.0.1:8000/api/token/refresh/
@api.route('/api/token/refresh/', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    cur_user_id = get_jwt_identity()
    user = User.query.get(cur_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_access_token = create_access_token(identity=str(user.id))
    new_refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify(access_token=new_access_token, refresh_token=new_refresh_token), 200
