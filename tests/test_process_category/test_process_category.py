from src.process_category.process_category import ProcessCategory
from src.process_category.enum_category import E_CATE, E_CATE_META_ELE
from category.category_action import CategoryAction


def test_process_category():
    pc = ProcessCategory()

    # when: category 등록
    pc.register_category()

    # cate1 콜백 실행 (cProcessCate.__registCateInfo + GetCateCallback 대응)
    pc.cate_reg_queue[E_CATE.DOWNLOADER]()

    # then: DOWNLOADER cate1 존재
    assert E_CATE.DOWNLOADER in pc.cate_queue

    downloader = pc.cate_queue[E_CATE.DOWNLOADER]

    # --- cate2 존재 여부 ---
    assert E_CATE.E_DOWNLOADER.LIDAR in downloader
    assert E_CATE.E_DOWNLOADER.CAMERA in downloader
    assert E_CATE.E_DOWNLOADER.GNSS in downloader

    # --- cate3 (process) 확인 ---
    lidar = downloader[E_CATE.E_DOWNLOADER.LIDAR]

    process_name = E_CATE.E_DOWNLOADER.E_LIDAR.E_AT128_ROOF_FRONT[E_CATE_META_ELE.NAME]
    assert process_name in lidar

    action = lidar[process_name]

    action.invoke("app_name", "process_name")

    # CategoryAction 인스턴스인지
    assert isinstance(action, CategoryAction)

    # lambda(callable)인지
    assert callable(action.action)
