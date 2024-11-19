import { NextResponse } from 'next/server';

export async function GET() {
    const tripDetails = [
        {
            day: 1,
            time: "10:00 AM",
            theme: "Architectural",
            locations: [
                { lat: 51.4993, lng: -0.1273, name: "Westminster Abbey", reason: "Historic site with rich history", tips: "Arrive early to avoid crowds" },
                { lat: 51.5081, lng: -0.0759, name: "Tower of London", reason: "Historic site with rich history", tips: "Arrive early to avoid crowds" },
                { lat: 51.5138, lng: -0.0984, name: "St. Paul's Cathedral", reason: "Historic site with rich history", tips: "Arrive early to avoid crowds" }
            ]
        },
        {
            day: 2,
            time: "11:00 AM",
            theme: "Artistic",
            locations: [
                { lat: 51.5089, lng: -0.1283, name: "National Gallery", reason: "Historic site with rich history", tips: "Arrive early to avoid crowds" },
                { lat: 51.5076, lng: -0.0994, name: "Tate Modern", reason: "Historic site with rich history", tips: "Arrive early to avoid crowds" },
                { lat: 51.5081, lng: -0.0977, name: "Shakespeare's Globe", reason: "Historic site with rich history", tips: "Arrive early to avoid crowds" }
            ]
        }
    ];

    return NextResponse.json(tripDetails);
}
