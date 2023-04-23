LEVELS = {
    1: (1, 55.468117, 37.296497, 'фонтана', 37.295382, 37.298140, 55.467836, 55.469765),
    2: (2, 55.475614, 37.299292, 'волейбольной площадки', 37.297233, 37.300808, 55.474638, 55.476154),
    3: (1, 55.484520, 37.304923, 'фонтана', 37.304213, 37.308175, 55.484423, 55.486265),
    4: (0, 55.495157, 37.305522, 'уточки', 37.301554, 37.308184, 55.492380, 55.496271)
}


def predict_image(image, level):
    img = Image.open(image)
    transform_norm = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(244),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    # get normalized image
    img_normalized = transform_norm(img).float()
    img_normalized = img_normalized.unsqueeze_(0)
    # input = Variable(image_tensor)
    # print(img_normalized.shape)
    with torch.no_grad():
        model.eval()
        output = model(img_normalized)
        p = torch.nn.functional.softmax(output, dim=1)
        probs = [p[0][0].item(), p[0][1].item(), p[0][2].item()]
        max_ind = probs.index(max(probs))
        print(probs)
        print(max_ind)
        if LEVELS[level][0] == max_ind and max(probs) > 0.75:
            return True
        else:
            return False


def check_keys(keys):
    global DB
    result = []
    db = sqlite3.connect(DB)
    cursor = db.cursor()
    request = f'''SELECT * FROM {keys[0]}'''
    data = cursor.execute(request).fetchall()
    keys_tokens = set(keys[1])
    print(keys, 'cccc', data)
    print('НАШИ КЛЮЧИ--------------------------------------------------------------------------------')
    for obj in data:
        obj_tokens = set(obj[-1].split())
        print(keys_tokens, '   ', obj_tokens)
        if keys_tokens.issubset(obj_tokens):
            result.append(obj)
    print(result)
    db.close()
    return result


def get_coordinates(place, keys):
    coordinates = []
    print(place, 'ВНУТРИ ФУНКЦИИ')
    db = sqlite3.connect('ex.db')
    cursor = db.cursor()
    request = f'''SELECT coords FROM {keys[0]} WHERE name = ?'''
    coors = cursor.execute(request, (place,)).fetchall()
    # print(coors[0][0])
    coordinates.append(coors[0][0].split(', '))
    print(coordinates)
    db.close()
    return coordinates
