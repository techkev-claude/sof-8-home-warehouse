from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from app.database import get_session
from app.models.location import Location
from app.models.item import Item
from app.schemas.location import LocationCreate, LocationUpdate, LocationRead, LocationTreeNode
from app.security import get_current_user, require_member

router = APIRouter(
    prefix="/locations", tags=["locations"], dependencies=[Depends(get_current_user)]
)


def _build_tree(locations: List[Location], parent_id: Optional[int] = None) -> List[LocationTreeNode]:
    nodes = []
    for loc in locations:
        if loc.parent_id == parent_id:
            node = LocationTreeNode.model_validate(loc)
            node.children = _build_tree(locations, loc.id)
            nodes.append(node)
    return nodes


@router.get("/", response_model=List[LocationRead])
def list_locations(session: Session = Depends(get_session)):
    """Flache Liste aller Orte (z.B. fuer Dropdowns)."""
    return session.exec(select(Location)).all()


@router.get("/tree", response_model=List[LocationTreeNode])
def get_location_tree(session: Session = Depends(get_session)):
    """Hierarchischer Baum fuer die Drill-Down-Navigation in der UI."""
    locations = session.exec(select(Location)).all()
    return _build_tree(list(locations))


@router.post("/", response_model=LocationRead, status_code=201, dependencies=[Depends(require_member)])
def create_location(data: LocationCreate, session: Session = Depends(get_session)):
    if data.parent_id is not None and not session.get(Location, data.parent_id):
        raise HTTPException(status_code=404, detail="Parent location not found")
    location = Location(**data.dict())
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


@router.patch("/{location_id}", response_model=LocationRead, dependencies=[Depends(require_member)])
def update_location(location_id: int, data: LocationUpdate, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    update_data = data.dict(exclude_unset=True)
    if update_data.get("parent_id") == location_id:
        raise HTTPException(status_code=400, detail="Location cannot be its own parent")
    for key, val in update_data.items():
        setattr(location, key, val)
    session.commit()
    session.refresh(location)
    return location


@router.delete("/{location_id}", status_code=204, dependencies=[Depends(require_member)])
def delete_location(location_id: int, session: Session = Depends(get_session)):
    location = session.get(Location, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    in_use = session.exec(select(Item).where(Item.location_id == location_id)).first()
    if in_use:
        raise HTTPException(status_code=409, detail="Location is still in use by items")
    has_children = session.exec(select(Location).where(Location.parent_id == location_id)).first()
    if has_children:
        raise HTTPException(status_code=409, detail="Location has child locations")
    session.delete(location)
    session.commit()
