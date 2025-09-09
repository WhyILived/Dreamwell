"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Globe, LogOut, Plus, Sparkles, X } from "lucide-react"
import { useAuth } from "@/lib/auth-context"

export default function BrandProfilePage() {
  const [brandData, setBrandData] = useState({
    companyName: "",
    website: "",
    keywords: [] as string[],
  })
  const [countryCode, setCountryCode] = useState<string>("")
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([])
  const [newKeyword, setNewKeyword] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  // Influencer search moved to Influencers tab
  
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
      const keywords = user.keywords ? user.keywords.split(',').map(k => k.trim()).filter(k => k) : []
      setBrandData({
        companyName: user.company_name || "",
        website: user.website || "",
        keywords: keywords,
      })
      setCountryCode((user as any).country_code || "")
      setSelectedKeywords(keywords)
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
        keywords: selectedKeywords.join(', '),
        country_code: countryCode || null,
      })
      alert("Profile updated successfully!")
    } catch (error) {
      console.error("Failed to update profile:", error)
      alert("Failed to update profile. Please try again.")
    }
  }

  const handleAddKeyword = async () => {
    if (newKeyword.trim() && !brandData.keywords.includes(newKeyword.trim())) {
      const updatedKeywords = [...brandData.keywords, newKeyword.trim()]
      setBrandData(prev => ({ ...prev, keywords: updatedKeywords }))
      
      // Save to database
      try {
        await updateProfile({
          company_name: brandData.companyName,
          website: brandData.website,
          keywords: updatedKeywords.join(', '),
        })
        setNewKeyword("")
      } catch (error) {
        console.error("Failed to save keyword:", error)
        alert("Failed to save keyword. Please try again.")
      }
    }
  }

  const handleRemoveKeyword = async (keyword: string) => {
    const updatedKeywords = brandData.keywords.filter(k => k !== keyword)
    setBrandData(prev => ({ ...prev, keywords: updatedKeywords }))
    setSelectedKeywords(prev => prev.filter(k => k !== keyword))
    
    // Save to database
    try {
      await updateProfile({
        company_name: brandData.companyName,
        website: brandData.website,
        keywords: updatedKeywords.join(', '),
      })
    } catch (error) {
      console.error("Failed to remove keyword:", error)
      alert("Failed to remove keyword. Please try again.")
    }
  }

  const handleGenerateKeywords = async () => {
    if (!brandData.website) {
      alert("Please enter a website URL first")
      return
    }

    setIsGenerating(true)
    try {
      // Call the backend to generate company values from website
      const response = await fetch('http://localhost:5000/api/auth/generate-values', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          website: brandData.website,
          user_id: user?.id 
        }),
      })

      if (response.ok) {
        const data = await response.json()
        const generatedKeywords = data.values || []
        const allKeywords = generatedKeywords
        
        // Update the keywords from the database response
        setBrandData(prev => ({
          ...prev,
          keywords: allKeywords
        }))
        
        // Add new keywords to selected keywords as well
        setSelectedKeywords(prev => {
          const existingSelected = prev || []
          const newKeywords = generatedKeywords.filter((keyword: string) =>
            !existingSelected.includes(keyword)
          )
          return [...existingSelected, ...newKeywords]
        })
        
        alert(`Generated ${generatedKeywords.length} company values from your website!`)
      } else {
        throw new Error('Failed to generate company values')
      }
    } catch (error) {
      console.error("Failed to generate values:", error)
      alert("Failed to generate values. Please try again.")
    } finally {
      setIsGenerating(false)
    }
  }

  // Search moved to Influencers tab

  const handleKeywordToggle = (keyword: string, checked: boolean) => {
    if (checked) {
      setSelectedKeywords(prev => [...prev, keyword])
    } else {
      setSelectedKeywords(prev => prev.filter(k => k !== keyword))
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

      <div className="grid lg:grid-cols-1 gap-6">
        {/* Brand Information Form */}
        <div className="space-y-6">
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

              {/* Company Region */}
              <div className="space-y-2">
                <Label htmlFor="country">Company Region</Label>
                <select
                  id="country"
                  className="border rounded px-3 py-2 w-full bg-background"
                  value={countryCode}
                  onChange={(e) => setCountryCode(e.target.value)}
                >
                  <option value="">Select a country</option>
                  <option value="US">United States (US)</option>
                  <option value="CA">Canada (CA)</option>
                  <option value="GB">United Kingdom (GB)</option>
                  <option value="AU">Australia (AU)</option>
                  <option value="DE">Germany (DE)</option>
                  <option value="FR">France (FR)</option>
                  <option value="IN">India (IN)</option>
                  <option value="JP">Japan (JP)</option>
                  <option value="SG">Singapore (SG)</option>
                  <option value="BR">Brazil (BR)</option>
                </select>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="keywords">Company Values</Label>
                  <div className="flex space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleGenerateKeywords}
                      disabled={isGenerating || !brandData.website}
                    >
                      <Sparkles className="w-4 h-4 mr-2" />
                      {isGenerating ? "Generating..." : "Generate Values"}
                    </Button>
                  </div>
                </div>

                {/* Add new value */}
                <div className="flex space-x-2">
                  <Input
                    placeholder="Add a value..."
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleAddKeyword}
                    disabled={!newKeyword.trim()}
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>

                {/* Values list with checkboxes */}
                {brandData.keywords.length > 0 ? (
                  <div className="space-y-2">
                    <Label className="text-sm text-muted-foreground">Select keywords for influencer search:</Label>
                    <div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto border rounded-md p-3">
                      {brandData.keywords.map((keyword, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Checkbox
                            id={`keyword-${index}`}
                            checked={selectedKeywords.includes(keyword)}
                            onCheckedChange={(checked) => handleKeywordToggle(keyword, checked as boolean)}
                          />
                          <Label
                            htmlFor={`keyword-${index}`}
                            className="flex-1 text-sm cursor-pointer"
                          >
                            {keyword}
                          </Label>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveKeyword(keyword)}
                            className="h-6 w-6 p-0"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>No keywords yet. Add some manually or generate them from your website.</p>
                  </div>
                )}

                {/* Selected keywords summary */}
                {selectedKeywords.length > 0 && (
                  <div className="space-y-2">
                    <Label className="text-sm text-muted-foreground">Selected for search:</Label>
                    <div className="flex flex-wrap gap-2">
                      {selectedKeywords.map((keyword, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Save button */}
                <div className="flex">
                  <Button onClick={handleSave} variant="outline">Save Changes</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Influencer Results moved to Influencers tab */}
      </div>
    </div>
  )
}
