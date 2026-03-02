"""Analytics endpoints for garage dashboards."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from sqlalchemy.sql import label
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import List, Optional
import json

from app.database import get_db, DATABASE_URL
from app.models import Garage, CarListing, ImpressionLog, ViewLog, LeadLog

# Set to True to return mock data for development
USE_MOCK = False

router = APIRouter()


@router.get("/")
async def analytics_root():
    return {"message": "Analytics endpoints are working", "mock": USE_MOCK}


class DateMetric(BaseModel):
    date: str
    impressions: int
    views: int

    class Config:
        from_attributes = True


class VehicleMetric(BaseModel):
    vehicle: str
    views: int

    class Config:
        from_attributes = True


class ListingMetric(BaseModel):
    id: int
    name: str
    image: str
    dateListed: str
    status: str
    impressions: int
    views: int
    ctr: float

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_impressions: int
    total_views: int
    lead_conversions: int
    average_rank: float


@router.get("/summary/{garage_id}")
async def get_analytics_summary(
    garage_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get summary metrics for a garage."""
    if USE_MOCK:
        # Return mock data matching frontend expectations
        return AnalyticsSummary(
            total_impressions=28300,
            total_views=9600,
            lead_conversions=342,
            average_rank=4.2,
        )
    
    # Verify garage exists
    garage = await db.get(Garage, garage_id)
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Total impressions (search appearances)
    impression_stmt = select(func.count(ImpressionLog.id)).where(
        and_(
            ImpressionLog.garage_id == garage_id,
            ImpressionLog.created_at >= start_date,
        )
    )
    total_impressions = (await db.execute(impression_stmt)).scalar() or 0

    # Total views (listing clicks)
    view_stmt = select(func.count(ViewLog.id)).where(
        and_(
            ViewLog.garage_id == garage_id,
            ViewLog.created_at >= start_date,
        )
    )
    total_views = (await db.execute(view_stmt)).scalar() or 0

    # Lead conversions
    lead_stmt = select(func.count(LeadLog.id)).where(
        and_(
            LeadLog.garage_id == garage_id,
            LeadLog.created_at >= start_date,
        )
    )
    lead_conversions = (await db.execute(lead_stmt)).scalar() or 0

    # Average rank (average position in search results)
    rank_stmt = select(func.avg(ImpressionLog.position)).where(
        and_(
            ImpressionLog.garage_id == garage_id,
            ImpressionLog.created_at >= start_date,
            ImpressionLog.position.isnot(None),
        )
    )
    avg_rank_result = (await db.execute(rank_stmt)).scalar()
    average_rank = round(float(avg_rank_result), 1) if avg_rank_result else 0.0

    return AnalyticsSummary(
        total_impressions=total_impressions,
        total_views=total_views,
        lead_conversions=lead_conversions,
        average_rank=average_rank,
    )


@router.get("/impressions-vs-views/{garage_id}")
async def get_impressions_vs_views(
    garage_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get daily impressions and views for the last N days."""
    if USE_MOCK:
        # Mock data matching frontend
        mock_data = [
            {"date": "2025-02-01", "impressions": 2400, "views": 400},
            {"date": "2025-02-02", "impressions": 1398, "views": 300},
            {"date": "2025-02-03", "impressions": 9800, "views": 2000},
            {"date": "2025-02-04", "impressions": 3908, "views": 1000},
            {"date": "2025-02-05", "impressions": 4800, "views": 800},
            {"date": "2025-02-06", "impressions": 3800, "views": 900},
            {"date": "2025-02-07", "impressions": 4300, "views": 1200},
            {"date": "2025-02-08", "impressions": 5200, "views": 1400},
            {"date": "2025-02-09", "impressions": 6100, "views": 1800},
            {"date": "2025-02-10", "impressions": 7300, "views": 2200},
            {"date": "2025-02-11", "impressions": 8400, "views": 2500},
            {"date": "2025-02-12", "impressions": 9200, "views": 2800},
            {"date": "2025-02-13", "impressions": 10200, "views": 3200},
            {"date": "2025-02-14", "impressions": 11300, "views": 3500},
            {"date": "2025-02-15", "impressions": 12400, "views": 3800},
            {"date": "2025-02-16", "impressions": 13500, "views": 4100},
            {"date": "2025-02-17", "impressions": 14200, "views": 4400},
            {"date": "2025-02-18", "impressions": 15100, "views": 4800},
            {"date": "2025-02-19", "impressions": 16200, "views": 5200},
            {"date": "2025-02-20", "impressions": 17300, "views": 5600},
            {"date": "2025-02-21", "impressions": 18400, "views": 6000},
            {"date": "2025-02-22", "impressions": 19500, "views": 6400},
            {"date": "2025-02-23", "impressions": 20600, "views": 6800},
            {"date": "2025-02-24", "impressions": 21700, "views": 7200},
            {"date": "2025-02-25", "impressions": 22800, "views": 7600},
            {"date": "2025-02-26", "impressions": 23900, "views": 8000},
            {"date": "2025-02-27", "impressions": 25000, "views": 8400},
            {"date": "2025-02-28", "impressions": 26100, "views": 8800},
            {"date": "2025-02-29", "impressions": 27200, "views": 9200},
            {"date": "2025-03-01", "impressions": 28300, "views": 9600},
        ]
        # Return only last N days (simplified)
        return [DateMetric(**item) for item in mock_data[-days:]]
    
    garage = await db.get(Garage, garage_id)
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    # Determine dialect from DATABASE_URL
    is_sqlite = DATABASE_URL.startswith('sqlite')

    if is_sqlite:
        # SQLite compatible query
        query = text("""
            SELECT 
                date(created_at) as date,
                COUNT(CASE WHEN log_type = 'impression' THEN 1 END) as impressions,
                COUNT(CASE WHEN log_type = 'view' THEN 1 END) as views
            FROM (
                SELECT created_at, 'impression' as log_type FROM impression_logs WHERE garage_id = :garage_id
                UNION ALL
                SELECT created_at, 'view' as log_type FROM view_logs WHERE garage_id = :garage_id
            ) combined_logs
            WHERE created_at >= date('now', '-' || :days || ' days')
            GROUP BY date(created_at)
            ORDER BY date
        """)
    else:
        # PostgreSQL query
        query = text("""
            SELECT 
                date_trunc('day', created_at) as date,
                COUNT(CASE WHEN log_type = 'impression' THEN 1 END) as impressions,
                COUNT(CASE WHEN log_type = 'view' THEN 1 END) as views
            FROM (
                SELECT created_at, 'impression' as log_type FROM impression_logs WHERE garage_id = :garage_id
                UNION ALL
                SELECT created_at, 'view' as log_type FROM view_logs WHERE garage_id = :garage_id
            ) combined_logs
            WHERE created_at >= NOW() - INTERVAL ':days days'
            GROUP BY date_trunc('day', created_at)
            ORDER BY date
        """)

    result = await db.execute(query, {"garage_id": garage_id, "days": days})
    rows = result.fetchall()

    # Format as list of DateMetric
    metrics = []
    for row in rows:
        if isinstance(row.date, str):
            date_str = row.date
        else:
            date_str = row.date.strftime("%Y-%m-%d")
        metrics.append(DateMetric(
            date=date_str,
            impressions=row.impressions or 0,
            views=row.views or 0,
        ))

    return metrics


@router.get("/top-vehicles/{garage_id}")
async def get_top_vehicles(
    garage_id: int,
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Get top performing vehicles by view count."""
    if USE_MOCK:
        # Mock data matching frontend
        mock_data = [
            {"vehicle": "Tesla Model 3", "views": 12500},
            {"vehicle": "Ford Mustang", "views": 9800},
            {"vehicle": "BMW X5", "views": 7600},
            {"vehicle": "Toyota Camry", "views": 5400},
            {"vehicle": "Honda Civic", "views": 3200},
        ]
        return [VehicleMetric(**item) for item in mock_data[:limit]]
    
    garage = await db.get(Garage, garage_id)
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    start_date = datetime.utcnow() - timedelta(days=days)

    query = text("""
        SELECT 
            cl.id,
            cl.title as vehicle,
            COUNT(vl.id) as views
        FROM view_logs vl
        JOIN car_listings cl ON vl.listing_id = cl.id
        WHERE vl.garage_id = :garage_id
          AND vl.created_at >= :start_date
        GROUP BY cl.id, cl.title
        ORDER BY views DESC
        LIMIT :limit
    """)

    result = await db.execute(
        query,
        {"garage_id": garage_id, "start_date": start_date, "limit": limit}
    )
    rows = result.fetchall()

    return [
        VehicleMetric(vehicle=row.vehicle, views=row.views or 0)
        for row in rows
    ]


@router.get("/listings-performance/{garage_id}")
async def get_listings_performance(
    garage_id: int,
    days: int = Query(30, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed performance metrics for each listing."""
    if USE_MOCK:
        # Mock data matching frontend
        mock_data = [
            {"id": 1, "name": "Tesla Model 3", "image": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=150&h=150&fit=crop", "dateListed": "2025-02-15", "status": "Live", "impressions": 12500, "views": 1250, "ctr": 10.0},
            {"id": 2, "name": "Ford Mustang", "image": "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=150&h=150&fit=crop", "dateListed": "2025-02-14", "status": "Live", "impressions": 9800, "views": 980, "ctr": 10.0},
            {"id": 3, "name": "BMW X5", "image": "https://images.unsplash.com/photo-1555212697-194d092e3b8f?w=150&h=150&fit=crop", "dateListed": "2025-02-13", "status": "Live", "impressions": 7600, "views": 760, "ctr": 10.0},
            {"id": 4, "name": "Toyota Camry", "image": "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=150&h=150&fit=crop", "dateListed": "2025-02-12", "status": "Live", "impressions": 5400, "views": 540, "ctr": 10.0},
            {"id": 5, "name": "Honda Civic", "image": "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?w=150&h=150&fit=crop", "dateListed": "2025-02-11", "status": "Live", "impressions": 3200, "views": 320, "ctr": 10.0},
            {"id": 6, "name": "Mercedes C-Class", "image": "https://images.unsplash.com/photo-1563720223485-8d6d5c5c8c1a?w=150&h=150&fit=crop", "dateListed": "2025-02-10", "status": "Live", "impressions": 2800, "views": 280, "ctr": 10.0},
            {"id": 7, "name": "Audi A4", "image": "https://images.unsplash.com/photo-1553440569-bcc63803a83d?w=150&h=150&fit=crop", "dateListed": "2025-02-09", "status": "Live", "impressions": 2400, "views": 240, "ctr": 10.0},
            {"id": 8, "name": "Volkswagen Golf", "image": "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=150&h=150&fit=crop", "dateListed": "2025-02-08", "status": "Live", "impressions": 2000, "views": 200, "ctr": 10.0},
        ]
        return [ListingMetric(**item) for item in mock_data[skip:skip+limit]]
    
    garage = await db.get(Garage, garage_id)
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found")

    start_date = datetime.utcnow() - timedelta(days=days)

    is_sqlite = DATABASE_URL.startswith('sqlite')
    
    if is_sqlite:
        # SQLite syntax: LIMIT before OFFSET
        query = text("""
            SELECT 
                cl.id,
                cl.title as name,
                COALESCE(cl.images, '[]') as images,
                cl.created_at as date_listed,
                'Live' as status,
                COUNT(DISTINCT il.id) as impressions,
                COUNT(DISTINCT vl.id) as views,
                CASE 
                    WHEN COUNT(DISTINCT il.id) > 0 
                    THEN ROUND(COUNT(DISTINCT vl.id) * 100.0 / COUNT(DISTINCT il.id), 1)
                    ELSE 0
                END as ctr
            FROM car_listings cl
            LEFT JOIN impression_logs il ON il.listing_id = cl.id 
                AND il.garage_id = :garage_id
                AND il.created_at >= :start_date
            LEFT JOIN view_logs vl ON vl.listing_id = cl.id 
                AND vl.garage_id = :garage_id
                AND vl.created_at >= :start_date
            WHERE cl.garage_id = :garage_id
            GROUP BY cl.id, cl.title, cl.images, cl.created_at
            ORDER BY impressions DESC
            LIMIT :limit
            OFFSET :skip
        """)
    else:
        # PostgreSQL syntax: OFFSET before LIMIT
        query = text("""
            SELECT 
                cl.id,
                cl.title as name,
                COALESCE(cl.images, '[]') as images,
                cl.created_at as date_listed,
                'Live' as status,
                COUNT(DISTINCT il.id) as impressions,
                COUNT(DISTINCT vl.id) as views,
                CASE 
                    WHEN COUNT(DISTINCT il.id) > 0 
                    THEN ROUND(COUNT(DISTINCT vl.id) * 100.0 / COUNT(DISTINCT il.id), 1)
                    ELSE 0
                END as ctr
            FROM car_listings cl
            LEFT JOIN impression_logs il ON il.listing_id = cl.id 
                AND il.garage_id = :garage_id
                AND il.created_at >= :start_date
            LEFT JOIN view_logs vl ON vl.listing_id = cl.id 
                AND vl.garage_id = :garage_id
                AND vl.created_at >= :start_date
            WHERE cl.garage_id = :garage_id
            GROUP BY cl.id, cl.title, cl.images, cl.created_at
            ORDER BY impressions DESC
            OFFSET :skip
            LIMIT :limit
        """)

    result = await db.execute(
        query,
        {
            "garage_id": garage_id,
            "start_date": start_date,
            "skip": skip,
            "limit": limit,
        }
    )
    rows = result.fetchall()

    listings = []
    for row in rows:
        # Parse first image from JSON array if available
        image_url = "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=150&h=150&fit=crop"
        try:
            if row.images and row.images != "[]":
                images = json.loads(row.images)
                if images and len(images) > 0:
                    image_url = images[0]
        except:
            pass

        listings.append(ListingMetric(
            id=row.id,
            name=row.name,
            image=image_url,
            dateListed=row.date_listed.strftime("%Y-%m-%d"),
            status=row.status,
            impressions=row.impressions or 0,
            views=row.views or 0,
            ctr=row.ctr or 0.0,
        ))

    return listings


class LeadRequest(BaseModel):
    listing_id: int
    contact_method: str = "form"  # "phone", "email", "form"
    user_session: Optional[str] = None


@router.post("/lead")
async def log_lead(
    request: LeadRequest,
    db: AsyncSession = Depends(get_db),
):
    """Log a lead conversion (user clicked Contact Dealer)."""
    # Get listing to determine garage_id
    result = await db.execute(
        select(CarListing).where(CarListing.id == request.listing_id)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if not listing.garage_id:
        raise HTTPException(status_code=400, detail="Listing has no garage")

    lead_log = LeadLog(
        garage_id=listing.garage_id,
        listing_id=listing.id,
        user_session=request.user_session,
        contact_method=request.contact_method,
    )
    db.add(lead_log)
    await db.commit()

    return {"status": "success", "message": "Lead logged"}