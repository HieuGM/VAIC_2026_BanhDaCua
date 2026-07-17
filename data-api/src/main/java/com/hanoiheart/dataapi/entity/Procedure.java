package com.hanoiheart.dataapi.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;

/**
 * Quy trình SOP (e.g. QT.25.01 đón tiếp bệnh nhân khu TN1 CS1). Each row is one
 * step; {@code code+step_no} is unique.
 */
@Entity
@Table(name = "procedures", schema = "hospital")
public class Procedure extends BaseEntity {

    @Column(name = "code", nullable = false, length = 32)
    private String code;

    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "step_no", nullable = false)
    private Integer stepNo;

    @Column(name = "name")
    private String name;

    @Column(name = "description", columnDefinition = "text")
    private String description;

    @Column(name = "responsible_role")
    private String responsibleRole;

    @Column(name = "related_form")
    private String relatedForm;

    @Column(name = "source_doc")
    private String sourceDoc;

    public String getCode() { return code; }
    public void setCode(String c) { this.code = c; }
    public String getTitle() { return title; }
    public void setTitle(String t) { this.title = t; }
    public Integer getStepNo() { return stepNo; }
    public void setStepNo(Integer s) { this.stepNo = s; }
    public String getName() { return name; }
    public void setName(String n) { this.name = n; }
    public String getDescription() { return description; }
    public void setDescription(String d) { this.description = d; }
    public String getResponsibleRole() { return responsibleRole; }
    public void setResponsibleRole(String r) { this.responsibleRole = r; }
    public String getRelatedForm() { return relatedForm; }
    public void setRelatedForm(String r) { this.relatedForm = r; }
    public String getSourceDoc() { return sourceDoc; }
    public void setSourceDoc(String s) { this.sourceDoc = s; }
}
