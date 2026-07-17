package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

import java.time.LocalDate;

/**
 * Chính sách Bảo hiểm Y tế (TT22/2023, TT13/2020, NQ45/2024...).
 */
@Entity
@Table(name = "bhyt_policies", schema = "hospital")
public class BhytPolicy extends BaseEntity {

    @Column(name = "code", nullable = false, unique = true, length = 64)
    private String code;

    @Column(name = "title", nullable = false)
    private String title;

    /** cardiac | chronic | cross_ref | copay | general. */
    @Column(name = "category", length = 32)
    private String category;

    @Column(name = "summary")
    private String summary;

    @Column(name = "details_md", columnDefinition = "text")
    private String detailsMd;

    @Column(name = "source_url")
    private String sourceUrl;

    @Column(name = "effective_date")
    private LocalDate effectiveDate;

    public String getCode() { return code; }
    public void setCode(String c) { this.code = c; }
    public String getTitle() { return title; }
    public void setTitle(String t) { this.title = t; }
    public String getCategory() { return category; }
    public void setCategory(String c) { this.category = c; }
    public String getSummary() { return summary; }
    public void setSummary(String s) { this.summary = s; }
    public String getDetailsMd() { return detailsMd; }
    public void setDetailsMd(String d) { this.detailsMd = d; }
    public String getSourceUrl() { return sourceUrl; }
    public void setSourceUrl(String s) { this.sourceUrl = s; }
    public LocalDate getEffectiveDate() { return effectiveDate; }
    public void setEffectiveDate(LocalDate d) { this.effectiveDate = d; }
}
