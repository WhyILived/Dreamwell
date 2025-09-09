"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Globe, LogOut } from "lucide-react"
import { useAuth } from "@/lib/auth-context"

export default function BrandProfilePage() {
  const [brandData, setBrandData] = useState({
    companyName: "",
    website: "",
    keywords: "",
  })
  
  const { user, isLoading, logout, updateProfile } = useAuth()
  const router = useRouter()

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  // Initialize brand data from user profile
  useEffect(() => {
    if (user) {
      setBrandData({
        companyName: user.company_name || "",
        website: user.website || "",
        keywords: user.keywords || "",
      })
    }
  }, [user])

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (!user) {
    return null
  }


  const handleSave = async () => {
    try {
      await updateProfile({
        company_name: brandData.companyName,
        website: brandData.website,
        keywords: brandData.keywords,
      })
      // Show success message or toast
      alert("Profile updated successfully!")
    } catch (error) {
      console.error("Failed to update profile:", error)
      alert("Failed to update profile. Please try again.")
    }
  }

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Brand Profile</h1>
          <p className="text-muted-foreground">
            Welcome back, {user.company_name || user.email}! Manage your brand information for better influencer matching
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>

      {/* Brand Information Form */}
      <div className="max-w-2xl">
          <Card>
            <CardHeader>
              <CardTitle>Company Information</CardTitle>
              <CardDescription>Update your brand details to improve influencer matching accuracy</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="companyName">Company Name</Label>
                <Input
                  id="companyName"
                  value={brandData.companyName}
                  onChange={(e) => setBrandData((prev) => ({ ...prev, companyName: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="website">Website URL</Label>
                <div className="flex space-x-2">
                  <Input
                    id="website"
                    value={brandData.website}
                    onChange={(e) => setBrandData((prev) => ({ ...prev, website: e.target.value }))}
                  />
                  <Button variant="outline" size="icon">
                    <Globe className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="keywords">Company Keywords</Label>
                <Textarea
                  id="keywords"
                  value={brandData.keywords}
                  onChange={(e) => setBrandData((prev) => ({ ...prev, keywords: e.target.value }))}
                  placeholder="Enter keywords that describe your brand, products, or services (e.g., sustainable fashion, tech gadgets, organic skincare)..."
                  rows={4}
                />
              </div>

              <Button onClick={handleSave} className="w-full">
                Save Changes
              </Button>
            </CardContent>
          </Card>
        </div>
    </div>
  )
}
