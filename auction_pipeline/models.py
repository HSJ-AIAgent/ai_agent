from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class SearchCriteria:
    city: str
    district: str
    property_type: str = "아파트"
    status: str = "진행물건"
    min_area: float = 40.0
    max_area: Optional[float] = None


@dataclass
class AuctionCase:
    case_no: str
    court: str
    address: str
    detail_url: str
    min_bid: int = 0
    appraisal_value: int = 0
    bid_date: str = ""
    status: str = ""
    tid: str = ""
    area_supply: float = 0.0
    area_land: float = 0.0


@dataclass
class PropertyDetails:
    case_no: str
    complex_name: str
    building_no: str
    unit_no: str
    floor: str
    area_supply: float
    area_private: float
    area_land: float
    land_status: str = ""
    building_status: str = ""
    tenant_info: str = ""
    registry_info: str = ""
    doc_paths: Dict[str, str] = field(default_factory=dict)


@dataclass
class LayoutInfo:
    layout_type: str
    rooms: int = 0
    bathrooms: int = 0
    maintenance_fee: int = 0
    active_listings: int = 0
    floor_plan_path: str = ""


@dataclass
class ListingItem:
    seq: int
    listing_no: str = ""
    complex_name: str = ""
    building: str = ""
    area: float = 0.0
    layout_type: str = ""
    floor: str = ""
    orientation: str = ""
    view: str = ""
    direction: str = ""
    price: int = 0
    reg_date: str = ""
    agency: str = ""
    notes: str = ""
    preferred_building: str = ""


@dataclass
class NaverData:
    complex_name: str
    complex_id: str = ""
    layout_info: List[LayoutInfo] = field(default_factory=list)
    listings: List[ListingItem] = field(default_factory=list)
    price_graph_path: str = ""
    jeonse_graph_path: str = ""
    unit_count: int = 0
    total_buildings: int = 0


@dataclass
class TransactionStat:
    year: int
    sale_count: int = 0
    jeonse_count: int = 0
    avg_sale_price: int = 0
    avg_jeonse_price: int = 0


@dataclass
class RecentTransaction:
    date: str
    floor: str = ""
    area: float = 0.0
    price: int = 0
    transaction_type: str = "매매"


@dataclass
class AsilData:
    complex_name: str
    target_area_type: str = ""
    annual_stats: List[TransactionStat] = field(default_factory=list)
    recent_transactions: List[RecentTransaction] = field(default_factory=list)


@dataclass
class Facility:
    name: str
    category: str
    distance_m: int = 0
    walk_time_min: int = 0


@dataclass
class SpatialData:
    case_no: str
    address: str
    complex_name: str = ""
    lat: float = 0.0
    lng: float = 0.0
    location_summary: str = ""
    facilities: List[Facility] = field(default_factory=list)
    map_overview_path: str = ""
    map_unit_path: str = ""
    hogangnono_floor_plan_path: str = ""
    hogangnono_unit_map_path: str = ""


@dataclass
class AssetIndex:
    case_no: str
    docs: Dict[str, str] = field(default_factory=dict)
    images: Dict[str, str] = field(default_factory=dict)
    verified: bool = False


@dataclass
class PriceAnalysis:
    base_price: int = 0
    floor_adjust: int = 0
    orientation_adjust: int = 0
    view_adjust: int = 0
    preferred_building_adjust: int = 0
    final_price: int = 0
    analysis_notes: str = ""
    comparable_listings: List[ListingItem] = field(default_factory=list)
    floor_comparison: List[ListingItem] = field(default_factory=list)
    orientation_comparison: List[ListingItem] = field(default_factory=list)
    preferred_comparison: List[ListingItem] = field(default_factory=list)


@dataclass
class CaseReport:
    auction_case: AuctionCase
    property_details: Optional[PropertyDetails] = None
    naver_data: Optional[NaverData] = None
    asil_data: Optional[AsilData] = None
    spatial_data: Optional[SpatialData] = None
    price_analysis: Optional[PriceAnalysis] = None
    asset_index: Optional[AssetIndex] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class ReportData:
    criteria: SearchCriteria
    cases: List[CaseReport] = field(default_factory=list)
    generated_at: str = ""
    output_path: str = ""
